from __future__ import annotations

import datetime as dt

from rayforce import _rayforce_c as r
from rayforce.ffi import FFI
from rayforce.types.base import Scalar
from rayforce.types.registry import TypeRegistry


class Time(Scalar):
    """
    Represents time as milliseconds since midnight.
    """

    type_code = -r.TYPE_TIME
    ray_name = "time"

    def _create_from_value(self, value: dt.time | int | str) -> r.RayObject:
        return FFI.init_time(value)

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
