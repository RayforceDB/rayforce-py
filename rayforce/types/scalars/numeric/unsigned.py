from __future__ import annotations

from rayforce import _rayforce_c as r
from rayforce.ffi import FFI
from rayforce.types import exceptions
from rayforce.types.base import Scalar
from rayforce.types.registry import TypeRegistry


class U8(Scalar):
    type_code = -r.TYPE_U8
    ray_name = "u8"

    def _create_from_value(self, value: int) -> r.RayObject:
        try:
            return FFI.init_u8(int(value))
        except OverflowError as e:
            raise exceptions.RayInitError("Invalid value for 8-bit unsigned integer") from e

    def to_python(self) -> int:
        return FFI.read_u8(self.ptr)


TypeRegistry.register(-r.TYPE_U8, U8)
