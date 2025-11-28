from __future__ import annotations

from rayforce import _rayforce_c as r
from rayforce.core.ffi import FFI
from rayforce.types.base import Scalar
from rayforce.types.registry import TypeRegistry


class F64(Scalar):
    """64-bit floating point number"""

    type_code = -r.TYPE_F64
    ray_name = "F64"

    def _create_from_value(self, value: float) -> r.RayObject:
        return FFI.init_f64(float(value))

    def to_python(self) -> float:
        return FFI.read_f64(self.ptr)


TypeRegistry.register(-r.TYPE_F64, F64)
