from __future__ import annotations

import typing as t

from rayforce import _rayforce_c as r
from rayforce import errors
from rayforce.ffi import FFI

if t.TYPE_CHECKING:
    from rayforce.types.base import RayObject
    from rayforce.types.fn import Fn
    from rayforce.types.null import Null
    from rayforce.types.operators import Operation
    from rayforce.types.table import Table


class TypeRegistry:
    _types: t.ClassVar[dict[int, type[RayObject | Operation | Null | Fn | Table]]] = {}
    _initialized: t.ClassVar[bool] = False

    @classmethod
    def register(
        cls, type_code: int, type_class: type[RayObject | Operation | Null | Fn | Table]
    ) -> None:
        if type_code in cls._types:
            existing = cls._types[type_code]
            if existing != type_class:
                raise errors.RayforceTypeRegistryError(
                    f"Type code {type_code} already registered to {existing.__name__}, "
                    f"cannot register {type_class.__name__}",
                )
        cls._types[type_code] = type_class

    @classmethod
    def get(cls, type_code: int) -> type[RayObject | Operation | Null | Fn | Table] | None:
        return cls._types.get(type_code)

    @classmethod
    def from_ptr(cls, ptr: r.RayObject) -> RayObject | Operation | type[Null] | Fn | Table:
        """
        IMPORTANT: Vectors have POSITIVE type codes, Scalars have NEGATIVE type codes
        If type_code > 0: it's a VECTOR (e.g., 3 = I16 vector, 6 = Symbol vector)
        If type_code < 0: it's a SCALAR (e.g., -3 = I16 scalar, -6 = Symbol scalar)
        """

        if not isinstance(ptr, r.RayObject):
            raise errors.RayforceTypeRegistryError(f"Expected RayObject, got {type(ptr)}")

        type_code = FFI.get_obj_type(ptr)
        if type_code in (r.TYPE_UNARY, r.TYPE_BINARY, r.TYPE_VARY):
            type_class = cls._types.get(type_code)

            if not type_class or not hasattr(type_class, "from_ptr"):
                raise errors.RayforceTypeRegistryError(f"Unregistered type: {type_code}")

            return type_class.from_ptr(ptr)

        if type_code > 0 and type_code not in (
            r.TYPE_DICT,
            r.TYPE_LIST,
            r.TYPE_TABLE,
            r.TYPE_LAMBDA,
        ):
            from rayforce.types import Null, String, Vector

            if type_code == r.TYPE_C8:
                return String(ptr=ptr)

            if type_code == r.TYPE_NULL:
                return Null  # type: ignore[return-value]

            return Vector(ptr=ptr, ray_type=cls._types.get(-type_code))  # type: ignore[arg-type]

        type_class = cls._types.get(type_code)

        if type_class is None:
            raise errors.RayforceTypeRegistryError(
                f"Unknown type code {type_code}. Type not registered in TypeRegistry."
            )

        return type_class(ptr=ptr)  # type: ignore[call-arg,return-value]

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
