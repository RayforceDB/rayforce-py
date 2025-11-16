from __future__ import annotations
import datetime as dt

from raypy import _rayforce as r
from raypy.core.ffi import FFI
from raypy.types.base import Scalar
from raypy.types.registry import TypeRegistry
from raypy.types import exceptions


class Timestamp(Scalar):
    """
    Represents a point in time with millisecond precision.
    """

    type_code = -r.TYPE_TIMESTAMP

    def _create_from_value(self, value: dt.datetime | int | str) -> r.RayObject:
        if isinstance(value, dt.datetime):
            # Convert to milliseconds since Unix epoch
            timestamp_ms = int(value.timestamp() * 1000)
            return FFI.init_timestamp(timestamp_ms)
        elif isinstance(value, int):
            return FFI.init_timestamp(value)
        elif isinstance(value, str):
            # Parse ISO format
            dt_obj = dt.datetime.fromisoformat(value)
            timestamp_ms = int(dt_obj.timestamp() * 1000)
            return FFI.init_timestamp(timestamp_ms)
        else:
            raise exceptions.RayInitException(
                f"Cannot create Timestamp from {type(value)}"
            )

    def to_python(self) -> dt.datetime:
        millis = FFI.read_timestamp(self.ptr)
        return dt.datetime.fromtimestamp(millis / 1000.0, tz=dt.timezone.utc)

    def to_millis(self) -> int:
        return FFI.read_timestamp(self.ptr)


TypeRegistry.register(-r.TYPE_TIMESTAMP, Timestamp)
