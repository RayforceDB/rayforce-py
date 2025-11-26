from __future__ import annotations

from raypy import _rayforce as r
from raypy.core.ffi import FFI
from raypy.types import exceptions
from raypy.types.base import Scalar
from raypy.types.registry import TypeRegistry


class U8(Scalar):
    """8-bit unsigned integer"""

    type_code = -r.TYPE_U8
    ray_name = "U8"

    def _create_from_value(self, value: int) -> r.RayObject:
        try:
            return FFI.init_u8(int(value))
        except OverflowError as e:
            raise exceptions.RayInitException from e

    def to_python(self) -> int:
        return FFI.read_u8(self.ptr)


TypeRegistry.register(-r.TYPE_U8, U8)
