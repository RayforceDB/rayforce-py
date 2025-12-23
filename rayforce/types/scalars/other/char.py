from __future__ import annotations

from rayforce import _rayforce_c as r
from rayforce.ffi import FFI
from rayforce.types.base import Scalar
from rayforce.types.registry import TypeRegistry


class C8(Scalar):
    type_code = -r.TYPE_C8
    ray_name = "c8"

    def _create_from_value(self, value: str) -> r.RayObject:
        return FFI.init_c8(value)

    def to_python(self) -> str:
        return FFI.read_c8(self.ptr)


TypeRegistry.register(-r.TYPE_C8, C8)
