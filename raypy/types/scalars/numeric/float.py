from __future__ import annotations

from raypy import _rayforce as r
from raypy.core.ffi import FFI
from raypy.types.base import Scalar
from raypy.types.registry import TypeRegistry


class F64(Scalar):
    """64-bit floating point number"""

    type_code = -r.TYPE_F64

    def _create_from_value(self, value: float) -> r.RayObject:
        return FFI.init_f64(float(value))

    def to_python(self) -> float:
        return FFI.read_f64(self.ptr)


TypeRegistry.register(-r.TYPE_F64, F64)
