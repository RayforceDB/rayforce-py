from __future__ import annotations

import struct
import typing as t

import numpy as np

from rayforce import _rayforce_c as r
from rayforce import errors, utils
from rayforce.ffi import FFI
from rayforce.types.base import (
    AggContainerMixin,
    AriphmeticContainerMixin,
    ComparisonContainerMixin,
    ElementAccessContainerMixin,
    FunctionalContainerMixin,
    IterableContainerMixin,
    RayObject,
    SearchContainerMixin,
    SetOperationContainerMixin,
    SortContainerMixin,
)
from rayforce.types.containers.list import List
from rayforce.types.operators import Operation
from rayforce.types.scalars.other.symbol import Symbol

_RAW_FORMATS: dict[int, tuple[str, int]] = {
    r.TYPE_U8: ("B", 1),
    r.TYPE_B8: ("b", 1),
    r.TYPE_I16: ("h", 2),
    r.TYPE_I32: ("i", 4),
    r.TYPE_I64: ("q", 8),
    r.TYPE_F64: ("d", 8),
    r.TYPE_DATE: ("i", 4),
    r.TYPE_TIME: ("i", 4),
    r.TYPE_TIMESTAMP: ("q", 8),
}
_NUMPY_TO_RAY: dict[str, int] = {
    "uint8": r.TYPE_U8,
    "bool": r.TYPE_B8,
    "int16": r.TYPE_I16,
    "int32": r.TYPE_I32,
    "int64": r.TYPE_I64,
    "float64": r.TYPE_F64,
}
# Epoch offset: rayforce uses 2000-01-01, numpy uses 1970-01-01
_EPOCH_OFFSET_DAYS = 10_957  # (2000-01-01 - 1970-01-01).days
_EPOCH_OFFSET_NS = _EPOCH_OFFSET_DAYS * 86_400 * 1_000_000_000

_NUMPY_DTYPES: dict[int, t.Any] = {
    r.TYPE_U8: np.uint8,
    r.TYPE_B8: np.bool_,
    r.TYPE_I16: np.int16,
    r.TYPE_I32: np.int32,
    r.TYPE_I64: np.int64,
    r.TYPE_F64: np.float64,
    r.TYPE_DATE: np.int32,
    r.TYPE_TIME: np.int32,
    r.TYPE_TIMESTAMP: np.int64,
}


class Vector(
    SortContainerMixin,
    IterableContainerMixin,
    AggContainerMixin,
    AriphmeticContainerMixin,
    ComparisonContainerMixin,
    ElementAccessContainerMixin,
    SetOperationContainerMixin,
    SearchContainerMixin,
    FunctionalContainerMixin,
):
    def __init__(
        self,
        items: t.Sequence[t.Any] | None = None,
        *,
        ptr: r.RayObject | None = None,
        ray_type: type[RayObject] | int | None = None,
        length: int | None = None,
    ):
        if ptr is not None:
            self.ptr = ptr
            self._validate_ptr(ptr)

        elif items is not None:
            if ray_type is None:
                if not items:
                    raise errors.RayforceInitError("Cannot infer vector type for empty items")
                ray_type = FFI.get_obj_type(utils.python_to_ray(items[0]))
            self.ptr = self._create_from_value(value=items, ray_type=ray_type)

        elif length is not None and ray_type is not None:
            type_code = abs(ray_type if isinstance(ray_type, int) else ray_type.type_code)
            self.ptr = FFI.init_vector(type_code, length)

        else:
            raise errors.RayforceInitError(
                "Vector requires either items, ptr, or (ray_type + length)",
            )

    def _create_from_value(  # type: ignore[override]
        self, value: t.Sequence[t.Any], ray_type: type[RayObject] | int
    ) -> r.RayObject:
        type_code = abs(ray_type if isinstance(ray_type, int) else ray_type.type_code)
        return FFI.init_vector(type_code, list(value))

    def to_python(self) -> list:
        return list(self)

    def __len__(self) -> int:
        return FFI.get_obj_length(self.ptr)

    def __getitem__(self, idx: int) -> t.Any:
        if idx < 0:
            idx = len(self) + idx
        if idx < 0 or idx >= len(self):
            raise errors.RayforceIndexError(f"Vector index out of range: {idx}")

        return utils.ray_to_python(FFI.at_idx(self.ptr, idx))

    def __setitem__(self, idx: int, value: t.Any) -> None:
        if idx < 0:
            idx = len(self) + idx
        if not 0 <= idx < len(self):
            raise errors.RayforceIndexError(f"Vector index out of range: {idx}")

        FFI.insert_obj(iterable=self.ptr, idx=idx, ptr=utils.python_to_ray(value))

    def __iter__(self) -> t.Iterator[t.Any]:
        for i in range(len(self)):
            yield self[i]

    def to_list(self) -> list:
        fmt_info = _RAW_FORMATS.get(FFI.get_obj_type(self.ptr))
        if fmt_info is None:
            return [el.value for el in self]  # Fallback
        fmt_char, _ = fmt_info
        return list(struct.unpack(f"<{len(self)}{fmt_char}", FFI.read_vector_raw(self.ptr)))

    def to_numpy(self) -> t.Any:
        type_code = FFI.get_obj_type(self.ptr)
        dtype = _NUMPY_DTYPES.get(type_code)
        if dtype is None:
            return np.array(self.to_list())
        raw = np.frombuffer(FFI.read_vector_raw(self.ptr), dtype=dtype)
        if type_code == r.TYPE_TIMESTAMP:
            return (raw + _EPOCH_OFFSET_NS).view("datetime64[ns]")
        if type_code == r.TYPE_DATE:
            return (raw.astype(np.int64) + _EPOCH_OFFSET_DAYS).astype("datetime64[D]")
        if type_code == r.TYPE_TIME:
            return raw.astype("timedelta64[ms]")
        return raw

    @classmethod
    def from_numpy(cls, arr: t.Any, *, ray_type: type[RayObject] | int | None = None) -> Vector:
        if not isinstance(arr, np.ndarray):
            raise errors.RayforceInitError("from_numpy requires a numpy ndarray")

        arr = np.ascontiguousarray(arr)

        if ray_type is not None:
            type_code = abs(ray_type if isinstance(ray_type, int) else ray_type.type_code)
            return cls(ptr=FFI.init_vector_from_raw_buffer(type_code, len(arr), arr.data))

        if (maybe_code := _NUMPY_TO_RAY.get(arr.dtype.name)) is not None:
            return cls(ptr=FFI.init_vector_from_raw_buffer(maybe_code, len(arr), arr.data))

        # datetime64 -> Timestamp or Date
        if arr.dtype.kind == "M":
            resolution = np.datetime_data(arr.dtype)[0]
            if resolution == "D":
                int_arr = (arr.view(np.int64) - _EPOCH_OFFSET_DAYS).astype(np.int32)
                return cls(
                    ptr=FFI.init_vector_from_raw_buffer(r.TYPE_DATE, len(int_arr), int_arr.data)
                )
            # Any other resolution -> convert to ns -> Timestamp
            ns_arr = arr.astype("datetime64[ns]").view(np.int64) - _EPOCH_OFFSET_NS
            return cls(
                ptr=FFI.init_vector_from_raw_buffer(r.TYPE_TIMESTAMP, len(ns_arr), ns_arr.data)
            )

        # timedelta64 -> Time (milliseconds since midnight)
        if arr.dtype.kind == "m":
            arr_ms = arr.astype("timedelta64[ms]")
            int_arr = arr_ms.view(np.int64).astype(np.int32)
            return cls(ptr=FFI.init_vector_from_raw_buffer(r.TYPE_TIME, len(int_arr), int_arr.data))

        # String/object arrays
        if arr.dtype.kind in ("U", "S", "O"):
            return cls(items=arr.tolist(), ray_type=Symbol)

        raise errors.RayforceInitError(
            f"Cannot infer ray_type from numpy dtype '{arr.dtype.name}'. "
            f"Supported: {list(_NUMPY_TO_RAY.keys())}, datetime64, timedelta64, and string arrays. "
            f"Pass ray_type explicitly."
        )

    def reverse(self) -> Vector:
        return utils.eval_obj(List([Operation.REVERSE, self.ptr]))


class String(Vector):
    ptr: r.RayObject
    type_code = r.TYPE_C8

    def __init__(
        self, value: str | Vector | None = None, *, ptr: r.RayObject | None = None
    ) -> None:
        if ptr and (_type := FFI.get_obj_type(ptr)) != self.type_code:
            raise errors.RayforceInitError(
                f"Expected String RayObject (type {self.type_code}), got {_type}"
            )

        if isinstance(value, Vector):
            if (_type := FFI.get_obj_type(value.ptr)) != r.TYPE_C8:
                raise errors.RayforceInitError(
                    f"Expected Vector (type {self.type_code}), got {_type}"
                )
            self.ptr = value.ptr

        elif value is not None:
            super().__init__(ray_type=String, ptr=FFI.init_string(value))

        else:
            super().__init__(ptr=ptr)

    def to_python(self) -> str:  # type: ignore[override]
        return "".join(i.value for i in self)
