from __future__ import annotations
import datetime as dt

from raypy import _rayforce_c as r
from raypy.core.ffi import FFI
from raypy.types.base import Scalar
from raypy.types.registry import TypeRegistry
from raypy.types import exceptions


class Time(Scalar):
    """
    Represents time as milliseconds since midnight.
    """

    type_code = -r.TYPE_TIME
    ray_name = "Time"

    def _create_from_value(self, value: dt.time | int | str) -> r.RayObject:
        if isinstance(value, dt.time):
            millis = (
                value.hour * 3600000
                + value.minute * 60000
                + value.second * 1000
                + value.microsecond // 1000
            )
            return FFI.init_time(millis)
        elif isinstance(value, int):
            return FFI.init_time(value)
        elif isinstance(value, str):
            # Parse ISO format
            try:
                time_obj = dt.time.fromisoformat(value)
            except ValueError as e:
                raise exceptions.RayInitException from e
            millis = (
                time_obj.hour * 3600000
                + time_obj.minute * 60000
                + time_obj.second * 1000
                + time_obj.microsecond // 1000
            )
            return FFI.init_time(millis)
        else:
            raise exceptions.RayInitException(f"Cannot create Time from {type(value)}")

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
