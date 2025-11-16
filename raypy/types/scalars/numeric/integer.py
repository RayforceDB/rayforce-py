from __future__ import annotations

from raypy import _rayforce as r
from raypy.core.ffi import FFI
from raypy.types.base import Scalar
from raypy.types.registry import TypeRegistry


class I16(Scalar):
    """16-bit signed integer"""

    type_code = -r.TYPE_I16

    def _create_from_value(self, value: int) -> r.RayObject:
        return FFI.init_i16(int(value))

    def to_python(self) -> int:
        return FFI.read_i16(self.ptr)


class I32(Scalar):
    """32-bit signed integer"""

    type_code = -r.TYPE_I32

    def _create_from_value(self, value: int) -> r.RayObject:
        return FFI.init_i32(int(value))

    def to_python(self) -> int:
        return FFI.read_i32(self.ptr)


class I64(Scalar):
    """64-bit signed integer"""

    type_code = -r.TYPE_I64

    def _create_from_value(self, value: int) -> r.RayObject:
        return FFI.init_i64(int(value))

    def to_python(self) -> int:
        return FFI.read_i64(self.ptr)


TypeRegistry.register(-r.TYPE_I16, I16)
TypeRegistry.register(-r.TYPE_I32, I32)
TypeRegistry.register(-r.TYPE_I64, I64)
