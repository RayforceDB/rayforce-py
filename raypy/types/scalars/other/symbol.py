from __future__ import annotations

from raypy import _rayforce as r
from raypy.core.ffi import FFI
from raypy.types.base import Scalar
from raypy.types.registry import TypeRegistry


class Symbol(Scalar):
    type_code = -r.TYPE_SYMBOL
    ray_name = "Symbol"

    def _create_from_value(self, value: str) -> r.RayObject:
        return FFI.init_symbol(str(value))

    def to_python(self) -> str:
        return FFI.read_symbol(self.ptr)


class QuotedSymbol(Symbol):
    """
    QuotedSymbol is not registered separately as it shares the same type code as Symbol
    It's distinguished by an attribute, not by type code
    """

    def _create_from_value(self, value: str) -> r.RayObject:
        ptr = FFI.init_symbol(str(value))
        FFI.set_obj_attrs(ptr, 8)  # Quoted attribute
        return ptr


TypeRegistry.register(-r.TYPE_SYMBOL, Symbol)
