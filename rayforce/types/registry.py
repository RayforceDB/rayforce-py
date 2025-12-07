from __future__ import annotations

import typing as t

from rayforce import _rayforce_c as r
from rayforce.types import exceptions

if t.TYPE_CHECKING:
    from rayforce.types.base import RayObject
    from rayforce.types.operators import Operation


class TypeRegistry:
    _types: t.ClassVar[dict[int, type[RayObject | Operation]]] = {}
    _initialized: t.ClassVar[bool] = False

    @classmethod
    def register(cls, type_code: int, type_class: type[RayObject | Operation]) -> None:
        if type_code in cls._types:
            existing = cls._types[type_code]
            if existing != type_class:
                raise exceptions.RayTypeRegistryError(
                    f"Type code {type_code} already registered to {existing.__name__}, "
                    f"cannot register {type_class.__name__}",
                )
        cls._types[type_code] = type_class

    @classmethod
    def get(cls, type_code: int) -> type[RayObject | Operation] | None:
        return cls._types.get(type_code)

    @classmethod
    def from_ptr(cls, ptr: r.RayObject) -> RayObject | Operation:
        """
        IMPORTANT: Vectors have POSITIVE type codes, Scalars have NEGATIVE type codes
        If type_code > 0: it's a VECTOR (e.g., 3 = I16 vector, 6 = Symbol vector)
        If type_code < 0: it's a SCALAR (e.g., -3 = I16 scalar, -6 = Symbol scalar)
        """

        if not isinstance(ptr, r.RayObject):
            raise TypeError(f"Expected RayObject, got {type(ptr)}")

        type_code = ptr.get_obj_type()
        if type_code in (r.TYPE_UNARY, r.TYPE_BINARY, r.TYPE_VARY):
            type_class = cls._types.get(type_code)

            if not type_class:
                raise TypeError(f"Unregistered type: {type_code}")

            # TODO: Add lambda parsing here when lambdas are introduced

            return type_class.from_ptr(ptr)

        if type_code > 0 and type_code not in (r.TYPE_DICT, r.TYPE_LIST, r.TYPE_TABLE):
            from rayforce.types import String, Vector

            if type_code == r.TYPE_C8:
                return String(ptr=ptr)

            return Vector(ptr=ptr, ray_type=cls._types.get(-type_code))  # type: ignore[arg-type]

        type_class = cls._types.get(type_code)

        if type_class is None:
            raise TypeError(f"Unknown type code {type_code}. Type not registered in TypeRegistry.")

        return type_class(ptr=ptr)  # type: ignore[call-arg]

    @classmethod
    def is_registered(cls, type_code: int) -> bool:
        return type_code in cls._types

    @classmethod
    def list_registered_types(cls) -> dict[int, str]:
        return {code: type_class.__name__ for code, type_class in cls._types.items()}

    @classmethod
    def initialize(cls) -> None:
        if cls._initialized:
            return

        try:
            from rayforce import types  # noqa: F401

            cls._initialized = True
        except ImportError:
            pass
