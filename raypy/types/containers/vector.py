from __future__ import annotations
import typing as t

from raypy import _rayforce as r
from raypy.core.ffi import FFI
from raypy.types.base import Container
from raypy.types import exceptions


class Vector(Container):
    """
    Homogeneous vector type.
    """

    # Vectors don't have a single type_code - they use the element type code (positive)
    type_code: int | None = None

    def __init__(
        self,
        items: t.Sequence[t.Any] = None,
        *,
        ptr: r.RayObject | None = None,
        type_code: int | None = None,
        length: int | None = None,
    ):
        self._element_type_code = type_code

        if ptr is not None:
            self.ptr = ptr
            self._validate_ptr(ptr)
        elif items is not None:
            if type_code is None:
                raise exceptions.RayInitException(
                    "type_code required when creating Vector from value"
                )
            self.ptr = self._create_from_value(items)
        elif length is not None and type_code is not None:
            # Create empty vector with specified length
            self.ptr = FFI.init_vector(type_code, length)
        else:
            raise exceptions.RayInitException(
                "Vector requires either value, ptr, or (type_code + length)"
            )

    def _create_from_value(self, value: t.Sequence[t.Any]) -> r.RayObject:
        if self._element_type_code is None:
            raise exceptions.RayInitException(
                "Element type_code must be specified for Vector"
            )

        vec_ptr = FFI.init_vector(self._element_type_code, len(value))

        for idx, item in enumerate(value):
            if isinstance(item, Container) or hasattr(item, "ptr"):
                item_ptr = item.ptr
            else:
                from raypy.utils.conversion import python_to_ray

                item_ptr = python_to_ray(item)

            FFI.insert_obj(vec_ptr, idx, item_ptr)

        return vec_ptr

    def to_python(self) -> tuple:
        result = []
        for item in self:
            result.append(item)
        return tuple(result)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.type_code})"

    def __len__(self) -> int:
        return FFI.get_obj_length(self.ptr)

    def __getitem__(self, idx: int) -> t.Any:
        from raypy.utils.conversion import ray_to_python

        if idx < 0:
            idx = len(self) + idx
        if idx < 0 or idx >= len(self):
            raise IndexError(f"Vector index out of range: {idx}")

        return ray_to_python(FFI.at_idx(self.ptr, idx))

    def __setitem__(self, idx: int, value: t.Any) -> None:
        from raypy.utils.conversion import python_to_ray

        if idx < 0:
            idx = len(self) + idx

        if not 0 <= idx < len(self):
            raise IndexError("Vector index out of range")

        FFI.insert_obj(insert_to=self.ptr, idx=idx, ptr=python_to_ray(value))

    def __iter__(self) -> t.Iterator[t.Any]:
        for i in range(len(self)):
            yield self[i]


class String(Vector):
    """
    Vector of C8
    """

    ptr: r.RayObject

    type_code = r.TYPE_C8

    def __init__(
        self, value: str | None = None, *, ptr: r.RayObject | None = None
    ) -> None:
        # String is a vector of C8, so it should have POSITIVE type code (r.TYPE_C8)
        if ptr and (_type := ptr.get_obj_type()) != self.type_code:
            raise ValueError(
                f"Expected String RayObject (type {self.type_code}), got {_type}"
            )

        if value is not None:
            # Vectors have POSITIVE type codes, so use self.type_code directly (not negative!)
            super().__init__(
                type_code=self.type_code,  # r.TYPE_C8 is already positive
                items=[FFI.init_c8(i) for i in value],
            )
        else:
            super().__init__(ptr=ptr)

    @property
    def value(self) -> str:
        # Convert vector of C8 scalars to string
        result = []
        for i in range(len(self)):
            c8_item = self[i]
            # Each item should be a C8 scalar, get its character value
            if hasattr(c8_item, "to_python"):
                result.append(c8_item.to_python())
            elif hasattr(c8_item, "value"):
                result.append(c8_item.value)
            else:
                result.append(str(c8_item))
        return "".join(result)

    def __str__(self) -> str:
        return f"String({self.value})"

    def __repr__(self) -> str:
        return self.__str__()
