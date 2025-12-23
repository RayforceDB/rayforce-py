from __future__ import annotations

import datetime as dt

from rayforce import _rayforce_c as r
from rayforce.core.ffi import FFI
from rayforce.types.base import Scalar
from rayforce.types.registry import TypeRegistry

DATETIME_EPOCH = dt.datetime(2000, 1, 1, tzinfo=dt.UTC)


class Timestamp(Scalar):
    """
    Represents a point in time with millisecond precision.
    """

    type_code = -r.TYPE_TIMESTAMP
    ray_name = "timestamp"

    def _create_from_value(self, value: dt.datetime | int | str) -> r.RayObject:
        return FFI.init_timestamp(value)

    def to_python(self) -> dt.datetime:
        return DATETIME_EPOCH + dt.timedelta(microseconds=FFI.read_timestamp(self.ptr) // 1000)

    def to_millis(self) -> int:
        return FFI.read_timestamp(self.ptr)


TypeRegistry.register(-r.TYPE_TIMESTAMP, Timestamp)
