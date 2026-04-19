from __future__ import annotations

import struct
import typing as t
import uuid

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
    Scalar,
    SearchContainerMixin,
    SetOperationContainerMixin,
    SortContainerMixin,
)
from rayforce.types.containers.list import List
from rayforce.types.operators import Operation
from rayforce.types.scalars.numeric.unsigned import U8
from rayforce.types.scalars.other.symbol import Symbol

_RAW_FORMATS: dict[int, tuple[str, int]] = {
    r.TYPE_U8: ("B", 1),
    r.TYPE_B8: ("b", 1),
    r.TYPE_I16: ("h", 2),
    r.TYPE_I32: ("i", 4),
    r.TYPE_I64: ("q", 8),
    r.TYPE_F32: ("f", 4),
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
    "float32": r.TYPE_F32,
    "float64": r.TYPE_F64,
}
_RAY_TO_NUMPY: dict[int, str] = {
    r.TYPE_U8: "uint8",
    r.TYPE_B8: "bool",
    r.TYPE_I16: "int16",
    r.TYPE_I32: "int32",
    r.TYPE_I64: "int64",
    r.TYPE_F32: "float32",
    r.TYPE_F64: "float64",
}
# Auto-widen numpy dtypes that have no direct rayforce equivalent
_NUMPY_WIDEN: dict[str, str] = {
    "float16": "float32",
    "int8": "int16",
    "uint16": "int32",
    "uint32": "int64",
}
# Epoch offset: rayforce uses 2000-01-01, numpy uses 1970-01-01
_EPOCH_OFFSET_DAYS = 10_957  # (2000-01-01 - 1970-01-01).days
_EPOCH_OFFSET_NS = _EPOCH_OFFSET_DAYS * 86_400 * 1_000_000_000
_I32_NULL = np.int32(np.iinfo(np.int32).min)  # -2147483648
_I64_NULL = np.int64(np.iinfo(np.int64).min)  # iNaT

_NUMPY_DTYPES: dict[int, t.Any] = {
    r.TYPE_U8: np.uint8,
    r.TYPE_B8: np.bool_,
    r.TYPE_I16: np.int16,
    r.TYPE_I32: np.int32,
    r.TYPE_I64: np.int64,
    r.TYPE_F32: np.float32,
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

        vec_type = FFI.get_obj_type(self.ptr)

        # The C-level at_idx returns B8 scalars for U8 vector elements
        # because both are 1-byte types and the value loses precision (bool).
        # Read the correct byte value directly from the raw buffer instead.
        if vec_type == r.TYPE_U8:
            raw = FFI.read_vector_raw(self.ptr)
            return U8(raw[idx])

        # v2 has no RAY_F32 scalar atom, so collection_elem can't box F32 vec
        # elements. Read the raw bytes and widen to F64 for per-element access.
        if vec_type == r.TYPE_F32:
            from rayforce.types.scalars.numeric.float import F64

            raw = FFI.read_vector_raw(self.ptr)
            return F64(struct.unpack_from("<f", raw, idx * 4)[0])

        return utils.ray_to_python(FFI.at_idx(self.ptr, idx))

    def __setitem__(self, idx: int, value: t.Any) -> None:
        if idx < 0:
            idx = len(self) + idx
        if not 0 <= idx < len(self):
            raise errors.RayforceIndexError(f"Vector index out of range: {idx}")

        # Coerce plain Python values to the vector's element type so that
        # insert_obj receives a scalar whose type matches the vector.
        # Without this, e.g. inserting an int (I64) into an I16 vector
        # corrupts the vector type at the C level.
        from rayforce.types.null import Null
        from rayforce.types.registry import TypeRegistry

        vec_type = FFI.get_obj_type(self.ptr)
        scalar_class = TypeRegistry.get(-vec_type)
        if (
            scalar_class is not None
            and scalar_class is not Null
            and not isinstance(value, RayObject)
        ):
            ptr = scalar_class(value).ptr  # type: ignore[call-arg]
        else:
            ptr = utils.python_to_ray(value)

        FFI.set_obj(obj=self.ptr, idx=FFI.init_i64(idx), value=ptr)

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
            null_mask = raw == _I64_NULL
            if null_mask.any():
                adjusted = raw.copy()
                adjusted[null_mask] = 0
                result = (adjusted + _EPOCH_OFFSET_NS).view("datetime64[ns]").copy()
                result[null_mask] = np.datetime64("NaT")
                return result
            return (raw + _EPOCH_OFFSET_NS).view("datetime64[ns]")
        if type_code == r.TYPE_DATE:
            null_mask = raw == _I32_NULL
            if null_mask.any():
                safe = raw.astype(np.int64)
                safe[null_mask] = 0
                result = (safe + _EPOCH_OFFSET_DAYS).astype("datetime64[D]")
                result[null_mask] = np.datetime64("NaT")
                return result
            return (raw.astype(np.int64) + _EPOCH_OFFSET_DAYS).astype("datetime64[D]")
        if type_code == r.TYPE_TIME:
            null_mask = raw == _I32_NULL
            if null_mask.any():
                result = raw.astype("timedelta64[ms]").copy()
                result[null_mask] = np.timedelta64("NaT")
                return result
            return raw.astype("timedelta64[ms]")
        return raw

    @classmethod
    def from_numpy(cls, arr: t.Any, *, ray_type: type[RayObject] | int | None = None) -> Vector:
        if not isinstance(arr, np.ndarray):
            raise errors.RayforceInitError("from_numpy requires a numpy ndarray")

        if arr.ndim != 1:
            raise errors.RayforceInitError(
                f"from_numpy requires a 1-D array, got {arr.ndim}-D array with shape {arr.shape}"
            )

        arr = np.ascontiguousarray(arr)

        if ray_type is not None and arr.dtype.kind not in ("M", "m"):
            type_code = abs(ray_type if isinstance(ray_type, int) else ray_type.type_code)
            target_dtype = _RAY_TO_NUMPY.get(type_code)
            if target_dtype is not None and arr.dtype.name != target_dtype:
                arr = np.ascontiguousarray(arr.astype(target_dtype))
            return cls(ptr=FFI.init_vector_from_raw_buffer(type_code, len(arr), arr.data))

        if (maybe_code := _NUMPY_TO_RAY.get(arr.dtype.name)) is not None:
            return cls(ptr=FFI.init_vector_from_raw_buffer(maybe_code, len(arr), arr.data))

        # Auto-widen common dtypes (float32 → float64, int8 → int16)
        if (widen_to := _NUMPY_WIDEN.get(arr.dtype.name)) is not None:
            arr = arr.astype(widen_to)
            code = _NUMPY_TO_RAY[widen_to]
            return cls(ptr=FFI.init_vector_from_raw_buffer(code, len(arr), arr.data))

        # datetime64 -> Timestamp or Date
        if arr.dtype.kind == "M":
            resolution = np.datetime_data(arr.dtype)[0]
            if resolution == "D":
                raw_i64 = arr.view(np.int64)
                nat_mask = raw_i64 == _I64_NULL
                int_arr = (raw_i64 - _EPOCH_OFFSET_DAYS).astype(np.int32)
                if nat_mask.any():
                    int_arr[nat_mask] = _I32_NULL
                return cls(
                    ptr=FFI.init_vector_from_raw_buffer(r.TYPE_DATE, len(int_arr), int_arr.data)
                )
            # Any other resolution -> convert to ns -> Timestamp
            ns_view = arr.astype("datetime64[ns]").view(np.int64)
            nat_mask = ns_view == _I64_NULL
            ns_arr = ns_view.copy()
            ns_arr[~nat_mask] -= _EPOCH_OFFSET_NS
            # NaT positions keep int64 min (= rayforce null sentinel)
            return cls(
                ptr=FFI.init_vector_from_raw_buffer(r.TYPE_TIMESTAMP, len(ns_arr), ns_arr.data)
            )

        # timedelta64 -> Time (milliseconds since midnight)
        if arr.dtype.kind == "m":
            arr_ms = arr.astype("timedelta64[ms]")
            raw_i64 = arr_ms.view(np.int64)
            nat_mask = raw_i64 == _I64_NULL
            int_arr = raw_i64.astype(np.int32)
            if nat_mask.any():
                int_arr[nat_mask] = _I32_NULL
            return cls(ptr=FFI.init_vector_from_raw_buffer(r.TYPE_TIME, len(int_arr), int_arr.data))

        # String/object arrays
        if arr.dtype.kind in ("U", "S", "O"):
            items = arr.tolist()
            if arr.dtype.kind == "S":
                items = [x.decode() if isinstance(x, bytes) else x for x in items]
            # Detect UUID objects in object arrays → GUID vector
            if arr.dtype.kind == "O" and items and isinstance(items[0], uuid.UUID):
                from rayforce.types.scalars.other.guid import GUID

                return cls(items=items, ray_type=GUID)
            return cls(items=items, ray_type=Symbol)

        raise errors.RayforceInitError(
            f"Cannot infer ray_type from numpy dtype '{arr.dtype.name}'. "
            f"Supported: {list(_NUMPY_TO_RAY.keys())}, datetime64, timedelta64, and string arrays. "
            f"Pass ray_type explicitly."
        )

    def reverse(self) -> Vector:
        return utils.eval_obj(List([Operation.REVERSE, self.ptr]))


class String(Scalar):
    """v2 string atom (type -RAY_STR).

    Stored as a single RayObject atom — SSO for ≤7 bytes, pooled otherwise.
    Exposes len/iter/index helpers so call sites written against the old
    C8-vector shape continue to work at the Python layer.
    """

    type_code = -r.TYPE_STR
    ray_name = "str"

    def __init__(
        self,
        value: str | String | Vector | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        if ptr is not None:
            actual = FFI.get_obj_type(ptr)
            if actual != self.type_code:
                raise errors.RayforceInitError(
                    f"Expected String RayObject (type {self.type_code}), got {actual}"
                )
            self.ptr = ptr
            return

        if isinstance(value, String):
            self.ptr = value.ptr
            return

        if isinstance(value, Vector):
            # Legacy compatibility: a Vector pointing at a RAY_STR atom.
            if FFI.get_obj_type(value.ptr) != self.type_code:
                raise errors.RayforceInitError(
                    f"Expected Vector wrapping String (type {self.type_code}), "
                    f"got {FFI.get_obj_type(value.ptr)}"
                )
            self.ptr = value.ptr
            return

        if value is None:
            raise errors.RayforceInitError("String requires 'value' or 'ptr'")

        if not isinstance(value, str):
            raise errors.RayforceInitError(f"String expects str, got {type(value).__name__}")
        self.ptr = FFI.init_string(value)

    def _create_from_value(self, value: t.Any) -> r.RayObject:
        return FFI.init_string(value)

    def to_python(self) -> str:  # type: ignore[override]
        return FFI.read_string(self.ptr)

    def __len__(self) -> int:
        return FFI.get_obj_length(self.ptr)

    def __bool__(self) -> bool:
        return len(self) > 0

    def __getitem__(self, idx: int) -> String:
        py = self.to_python()
        if idx < 0:
            idx = len(py) + idx
        if idx < 0 or idx >= len(py):
            raise errors.RayforceIndexError(f"String index out of range: {idx}")
        return String(py[idx])

    def __iter__(self) -> t.Iterator[String]:
        for ch in self.to_python():
            yield String(ch)

    def to_numpy(self) -> t.Any:
        return np.array(list(self.to_python()))


from rayforce.types.registry import TypeRegistry  # noqa: E402

TypeRegistry.register(-r.TYPE_STR, String)
