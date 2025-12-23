from __future__ import annotations

from rayforce import _rayforce_c as r
from rayforce.ffi import FFI
from rayforce.types.base import Scalar
from rayforce.types.registry import TypeRegistry


class I16(Scalar):
    type_code = -r.TYPE_I16
    ray_name = "i16"

    def _create_from_value(self, value: int) -> r.RayObject:
        return FFI.init_i16(value)

    def to_python(self) -> int:
        return FFI.read_i16(self.ptr)


class I32(Scalar):
    type_code = -r.TYPE_I32
    ray_name = "i32"

    def _create_from_value(self, value: int) -> r.RayObject:
        return FFI.init_i32(value)

    def to_python(self) -> int:
        return FFI.read_i32(self.ptr)


class I64(Scalar):
    type_code = -r.TYPE_I64
    ray_name = "i64"

    def _create_from_value(self, value: int) -> r.RayObject:
        return FFI.init_i64(value)

    def to_python(self) -> int:
        return FFI.read_i64(self.ptr)


TypeRegistry.register(-r.TYPE_I16, I16)
TypeRegistry.register(-r.TYPE_I32, I32)
TypeRegistry.register(-r.TYPE_I64, I64)
