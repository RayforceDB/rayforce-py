from __future__ import annotations

from raypy import _rayforce_c as r
from raypy.core.ffi import FFI
from raypy.types.base import Scalar
from raypy.types.registry import TypeRegistry
from raypy.types import exceptions


class C8(Scalar):
    """Single character"""

    type_code = -r.TYPE_C8
    ray_name = "C8"

    def _create_from_value(self, value: str) -> r.RayObject:
        if not isinstance(value, str) or len(value) != 1:
            raise exceptions.RayInitException(
                f"C8 requires a single character, got {value!r}"
            )
        return FFI.init_c8(value)

    def to_python(self) -> str:
        return FFI.read_c8(self.ptr)


TypeRegistry.register(-r.TYPE_C8, C8)
