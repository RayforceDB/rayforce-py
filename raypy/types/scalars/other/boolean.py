from __future__ import annotations

from raypy import _rayforce as r
from raypy.core.ffi import FFI
from raypy.types.base import Scalar
from raypy.types.registry import TypeRegistry


class B8(Scalar):
    """Boolean value"""

    type_code = -r.TYPE_B8
    ray_name = "B8"

    def _create_from_value(self, value: bool) -> r.RayObject:
        return FFI.init_b8(bool(value))

    def to_python(self) -> bool:
        return FFI.read_b8(self.ptr)


TypeRegistry.register(-r.TYPE_B8, B8)
