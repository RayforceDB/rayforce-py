from __future__ import annotations

import datetime as dt

from rayforce import _rayforce_c as r
from rayforce import errors
from rayforce.ffi import FFI
from rayforce.types.base import Scalar, _eval_operation
from rayforce.types.registry import TypeRegistry

DATETIME_EPOCH = dt.datetime(2000, 1, 1, tzinfo=dt.UTC)


def tz_offset_nanos(tz: dt.tzinfo) -> int:
    """Convert a tzinfo to a signed nanosecond offset from UTC."""
    offset = tz.utcoffset(None)
    if offset is None:
        raise errors.RayforceValueError("Cannot determine UTC offset from provided tzinfo")
    return int(offset.total_seconds()) * 1_000_000_000


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

    def shift_tz(self, tz: dt.tzinfo) -> Timestamp:
        return _eval_operation("ADD", self, tz_offset_nanos(tz))


TypeRegistry.register(-r.TYPE_TIMESTAMP, Timestamp)
