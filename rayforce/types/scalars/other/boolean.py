from __future__ import annotations

from rayforce import _rayforce_c as r
from rayforce.core.ffi import FFI
from rayforce.types.base import Scalar
from rayforce.types.registry import TypeRegistry


class B8(Scalar):
    type_code = -r.TYPE_B8
    ray_name = "b8"

    def _create_from_value(self, value: bool) -> r.RayObject:
        return FFI.init_b8(bool(value))

    def to_python(self) -> bool:
        return FFI.read_b8(self.ptr)


TypeRegistry.register(-r.TYPE_B8, B8)
