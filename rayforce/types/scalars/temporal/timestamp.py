from __future__ import annotations

import datetime as dt

from rayforce import _rayforce_c as r
from rayforce.core.ffi import FFI
from rayforce.types import exceptions
from rayforce.types.base import Scalar
from rayforce.types.registry import TypeRegistry

epoch2000_py = dt.datetime(2000, 1, 1, tzinfo=dt.UTC)


def _datetime_to_ns(obj: dt.timedelta) -> int:
    return (
        obj.days * 24 * 3600 * 1_000_000_000
        + obj.seconds * 1_000_000_000
        + obj.microseconds * 1_000
    )


class Timestamp(Scalar):
    """
    Represents a point in time with millisecond precision.
    """

    type_code = -r.TYPE_TIMESTAMP
    ray_name = "Timestamp"

    def _create_from_value(self, value: dt.datetime | int | str) -> r.RayObject:
        if isinstance(value, dt.datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=dt.UTC)

            return FFI.init_timestamp(_datetime_to_ns(value - epoch2000_py))
        if isinstance(value, int):
            return FFI.init_timestamp(value)
        if isinstance(value, str):
            try:
                dt_obj = dt.datetime.fromisoformat(value)
            except ValueError as e:
                raise exceptions.RayInitError(f"Timestamp value is not isoformat: {value}") from e
            return FFI.init_timestamp(_datetime_to_ns(dt_obj - epoch2000_py))
        raise exceptions.RayInitError(f"Cannot create Timestamp from {type(value)}")

    def to_python(self) -> dt.datetime:
        return epoch2000_py + dt.timedelta(microseconds=FFI.read_timestamp(self.ptr) // 1000)

    def to_millis(self) -> int:
        return FFI.read_timestamp(self.ptr)


TypeRegistry.register(-r.TYPE_TIMESTAMP, Timestamp)
