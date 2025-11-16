from __future__ import annotations
import typing as t

from raypy import _rayforce as r
from raypy.types import exceptions

if t.TYPE_CHECKING:
    from raypy.types.base import RayObject


class TypeRegistry:
    """
    Central registry for all raypy types.
    """

    _types: dict[int, type[RayObject]] = {}
    _initialized: bool = False

    @classmethod
    def register(cls, type_code: int, type_class: type[RayObject]) -> None:
        if type_code in cls._types:
            existing = cls._types[type_code]
            if existing != type_class:
                raise exceptions.RayTypeRegistryException(
                    f"Type code {type_code} already registered to {existing.__name__}, "
                    f"cannot register {type_class.__name__}"
                )
        cls._types[type_code] = type_class

    @classmethod
    def get(cls, type_code: int) -> type[RayObject] | None:
        return cls._types.get(type_code)

    @classmethod
    def from_ptr(cls, ptr: r.RayObject) -> RayObject:
        """
        IMPORTANT: Vectors have POSITIVE type codes, Scalars have NEGATIVE type codes
        If type_code > 0: it's a VECTOR (e.g., 3 = I16 vector, 6 = Symbol vector)
        If type_code < 0: it's a SCALAR (e.g., -3 = I16 scalar, -6 = Symbol scalar)
        """

        if not isinstance(ptr, r.RayObject):
            raise Exception(f"Expected RayObject, got {type(ptr)}")

        type_code = ptr.get_obj_type()
        if type_code > 0 and type_code not in (r.TYPE_DICT, r.TYPE_LIST, r.TYPE_TABLE):
            from raypy.types import Vector

            return Vector(ptr=ptr, type_code=type_code)

        type_class = cls._types.get(type_code)

        if type_class is None:
            raise Exception(
                f"Unknown type code {type_code}. Type not registered in TypeRegistry."
            )

        return type_class(ptr=ptr)

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
            from raypy import types  # noqa: F401

            cls._initialized = True
        except ImportError:
            pass
