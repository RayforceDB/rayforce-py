from __future__ import annotations

import math
import struct

import numpy as np

from rayforce import _rayforce_c as r
from rayforce import errors
from rayforce.ffi import FFI
from rayforce.types.base import (
    AggScalarMixin,
    AriphmeticScalarMixin,
    ComparisonScalarMixin,
)
from rayforce.types.registry import TypeRegistry

_F32_MAX = 3.4028234663852886e38


class F32(AriphmeticScalarMixin, ComparisonScalarMixin, AggScalarMixin):
    """32-bit float scalar.

    v2 has no RAY_F32 atom; the value is stored in a length-1 RAY_F32 vector
    so the on-the-wire payload stays a real 32-bit float. Type code is the
    canonical scalar -RAY_F32 for registry lookup, but the underlying ptr's
    runtime type is +RAY_F32 (vector) — `_validate_ptr` accepts both.
    """

    type_code = -r.TYPE_F32
    ray_name = "f32"

    def _create_from_value(self, value: float) -> r.RayObject:
        try:
            v = float(value)
        except (TypeError, ValueError) as e:
            raise errors.RayforceInitError(f"Invalid value for F32: {value!r}") from e

        if math.isfinite(v) and abs(v) > _F32_MAX:
            raise errors.RayforceInitError(f"Value {v} overflows F32 (|x| > {_F32_MAX})")

        arr = np.array([v], dtype=np.float32)
        return FFI.init_vector_from_raw_buffer(r.TYPE_F32, 1, arr.data)

    def to_python(self) -> float:
        raw = FFI.read_vector_raw(self.ptr)
        return struct.unpack("<f", raw[:4])[0]

    def _validate_ptr(self, ptr: r.RayObject) -> None:
        if not isinstance(ptr, r.RayObject):
            raise errors.RayforceInitError(f"Expected RayObject, got {type(ptr)}")

        actual = FFI.get_obj_type(ptr)
        # Accept either a true F32 atom (future v2) or a length-1 F32 vector
        # (current workaround — v2 has no F32 atom ctor).
        if actual == -r.TYPE_F32:
            return
        if actual == r.TYPE_F32 and FFI.get_obj_length(ptr) == 1:
            return
        raise errors.RayforceInitError(
            f"F32 expects type code {-r.TYPE_F32} (atom) or a length-1 "
            f"{r.TYPE_F32} (vector), got type={actual}"
        )

    # v2 has no F32 arithmetic — promote both sides to F64 for binary numeric
    # ops so F32 ± F32 / F32 ± F64 produce sensible results (matches numpy
    # behavior in spirit: F32 widens to F64 when interacting with F64; here
    # we widen F32 unconditionally because v2 lacks F32 op kernels).
    def _as_f64(self):
        from rayforce.types.scalars.numeric.float import F64

        return F64(self.to_python())

    @staticmethod
    def _promote(value):
        return value._as_f64() if isinstance(value, F32) else value

    def __add__(self, other):
        return self._as_f64() + self._promote(other)

    def __radd__(self, other):
        return self._promote(other) + self._as_f64()

    def __sub__(self, other):
        return self._as_f64() - self._promote(other)

    def __rsub__(self, other):
        return self._promote(other) - self._as_f64()

    def __mul__(self, other):
        return self._as_f64() * self._promote(other)

    def __rmul__(self, other):
        return self._promote(other) * self._as_f64()

    def __truediv__(self, other):
        return self._as_f64() / self._promote(other)

    def __rtruediv__(self, other):
        return self._promote(other) / self._as_f64()

    def __floordiv__(self, other):
        return self._as_f64() // self._promote(other)

    def __rfloordiv__(self, other):
        return self._promote(other) // self._as_f64()

    def __mod__(self, other):
        return self._as_f64() % self._promote(other)


TypeRegistry.register(-r.TYPE_F32, F32)
