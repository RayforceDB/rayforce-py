from __future__ import annotations

import typing as t

from rayforce import _rayforce_c as r
from rayforce.types.registry import TypeRegistry


class _StaticRepr(type):
    def __repr__(cls) -> str:
        return "Null"

    def __bool__(cls) -> bool:
        return False

    def __eq__(cls, other: t.Any) -> bool:
        return (other is Null) or (other is None)

    __str__ = __repr__


class Null(metaclass=_StaticRepr):
    ptr = r.NULL_OBJ
    type_code = r.TYPE_NULL
    ray_name = "NULL"

    @staticmethod
    def to_python() -> None:
        return None


TypeRegistry.register(r.TYPE_NULL, Null)
