from __future__ import annotations

import typing as t

from rayforce import _rayforce_c as r
from rayforce import errors
from rayforce.ffi import FFI
from rayforce.types.base import Container, RayObject


class Vector(Container):
    def __init__(
        self,
        items: t.Sequence[t.Any] | None = None,
        *,
        ptr: r.RayObject | None = None,
        ray_type: type[RayObject] | int | None = None,
        length: int | None = None,
    ):
        self._element_ray_type = ray_type

        if ptr is not None:
            self.ptr = ptr
            self._validate_ptr(ptr)

        elif items is not None:
            if ray_type is None:
                raise errors.RayforceInitError("ray_type required when creating Vector from value")
            self.ptr = self._create_from_value(items)

        elif length is not None and ray_type is not None:
            type_code = ray_type if isinstance(ray_type, int) else ray_type.type_code
            self.ptr = FFI.init_vector(type_code, length)

        else:
            raise errors.RayforceInitError(
                "Vector requires either value, ptr, or (ray_type + length)",
            )

    def _create_from_value(self, value: t.Sequence[t.Any]) -> r.RayObject:
        if self._element_ray_type is None:
            raise errors.RayforceInitError("Element ray_type must be specified for Vector")

        type_code = (
            self._element_ray_type
            if isinstance(self._element_ray_type, int)
            else self._element_ray_type.type_code
        )

        ptr = FFI.init_vector(type_code=type_code, length=len(value))
        fill = list(value) if not isinstance(value, list) else value
        FFI.fill_vector(obj=ptr, fill=fill)
        return ptr

    def to_python(self) -> list:
        return list(self)

    def __len__(self) -> int:
        return FFI.get_obj_length(self.ptr)

    def __getitem__(self, idx: int) -> t.Any:
        from rayforce.utils.conversion import ray_to_python

        if idx < 0:
            idx = len(self) + idx
        if idx < 0 or idx >= len(self):
            raise errors.RayforceIndexError(f"Vector index out of range: {idx}")

        return ray_to_python(FFI.at_idx(self.ptr, idx))

    def __setitem__(self, idx: int, value: t.Any) -> None:
        from rayforce.utils.conversion import python_to_ray

        if idx < 0:
            idx = len(self) + idx
        if not 0 <= idx < len(self):
            raise errors.RayforceIndexError("Vector index out of range")

        FFI.insert_obj(iterable=self.ptr, idx=idx, ptr=python_to_ray(value))

    def __iter__(self) -> t.Iterator[t.Any]:
        for i in range(len(self)):
            yield self[i]


class String(Vector):
    ptr: r.RayObject
    type_code = r.TYPE_C8

    def __init__(
        self,
        value: str | Vector | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        if ptr and (_type := ptr.get_obj_type()) != self.type_code:
            raise errors.RayforceInitError(
                f"Expected String RayObject (type {self.type_code}), got {_type}"
            )

        if isinstance(value, Vector):
            if (_type := value.ptr.get_obj_type()) != r.TYPE_C8:
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
