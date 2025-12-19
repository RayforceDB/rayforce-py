from __future__ import annotations

import datetime as dt

from rayforce import _rayforce_c as r
from rayforce.core.ffi import FFI
from rayforce.types import exceptions
from rayforce.types.base import Scalar
from rayforce.types.registry import TypeRegistry


def _dt_time_to_ms(obj: dt.time) -> int:
    return obj.hour * 3600000 + obj.minute * 60000 + obj.second * 1000 + obj.microsecond // 1000


class Time(Scalar):
    """
    Represents time as milliseconds since midnight.
    """

    type_code = -r.TYPE_TIME
    ray_name = "time"

    def _create_from_value(self, value: dt.time | int | str) -> r.RayObject:
        if isinstance(value, dt.time):
            return FFI.init_time(_dt_time_to_ms(value))
        if isinstance(value, int):
            return FFI.init_time(value)
        if isinstance(value, str):
            try:
                time_obj = dt.time.fromisoformat(value)
            except ValueError as e:
                raise exceptions.RayInitError(f"Time value is not isoformat: {value}") from e
            return FFI.init_time(_dt_time_to_ms(time_obj))
        raise exceptions.RayInitError(f"Cannot create Time from {type(value)}")

    def to_python(self) -> dt.time:
        millis = FFI.read_time(self.ptr)
        hours = millis // 3600000
        millis %= 3600000
        minutes = millis // 60000
        millis %= 60000
        seconds = millis // 1000
        microseconds = (millis % 1000) * 1000
        return dt.time(hours, minutes, seconds, microseconds)

    def to_millis(self) -> int:
        return FFI.read_time(self.ptr)


TypeRegistry.register(-r.TYPE_TIME, Time)
