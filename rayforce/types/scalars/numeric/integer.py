from __future__ import annotations

from rayforce import _rayforce_c as r
from rayforce.ffi import FFI
from rayforce.types.base import (
    AggScalarMixin,
    AriphmeticScalarMixin,
    ComparisonScalarMixin,
)
from rayforce.types.registry import TypeRegistry

_I16_NULL = -(2**15)  # -32768 (0Nh)
_I32_NULL = -(2**31)  # -2147483648 (0Ni)
_I64_NULL = -(2**63)  # -9223372036854775808 (0Nj)


class I16(AriphmeticScalarMixin, ComparisonScalarMixin, AggScalarMixin):
    type_code = -r.TYPE_I16
    ray_name = "i16"

    def _create_from_value(self, value: int) -> r.RayObject:
        return FFI.init_i16(value)

    def to_python(self) -> int | None:
        val = FFI.read_i16(self.ptr)
        return None if val == _I16_NULL else val


class I32(AriphmeticScalarMixin, ComparisonScalarMixin, AggScalarMixin):
    type_code = -r.TYPE_I32
    ray_name = "i32"

    def _create_from_value(self, value: int) -> r.RayObject:
        return FFI.init_i32(value)

    def to_python(self) -> int | None:
        val = FFI.read_i32(self.ptr)
        return None if val == _I32_NULL else val


class I64(AriphmeticScalarMixin, ComparisonScalarMixin, AggScalarMixin):
    type_code = -r.TYPE_I64
    ray_name = "i64"

    def _create_from_value(self, value: int) -> r.RayObject:
        return FFI.init_i64(value)

    def to_python(self) -> int | None:
        val = FFI.read_i64(self.ptr)
        return None if val == _I64_NULL else val


TypeRegistry.register(-r.TYPE_I16, I16)
TypeRegistry.register(-r.TYPE_I32, I32)
TypeRegistry.register(-r.TYPE_I64, I64)
