import datetime as dt
from typing import Any

from raypy import _rayforce as r


class Time:
    """
    Rayforce Time class
    """

    ptr: r.RayObject

    ray_type_code = r.TYPE_TIME
    ray_init_method = "from_time"
    ray_extr_method = "get_time_value"

    def __init__(
        self,
        value: dt.date | int | str | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if ray_obj is not None:
            if (_type := ray_obj.get_type()) != -self.ray_type_code:
                raise ValueError(
                    f"Expected RayForce object of type {self.ray_type_code}, got {_type}"
                )
            self.ptr = ray_obj
            return

        ms_since_midnight = 0
        if value is None:
            now = dt.datetime.now()
            ms_since_midnight = (
                now.hour * 3600 + now.minute * 60 + now.second
            ) * 1000 + now.microsecond // 1000
        elif isinstance(value, int):
            if value < 0 or value > 86399999:  # 24*60*60*1000 - 1
                raise ValueError("Time value must be in range 0-86399999 milliseconds")
            ms_since_midnight = value
        elif isinstance(value, dt.time):
            ms_since_midnight = (
                value.hour * 3600 + value.minute * 60 + value.second
            ) * 1000 + value.microsecond // 1000
        elif isinstance(value, str):
            try:
                if "." in value:
                    # Parse with milliseconds
                    time_obj = dt.time.fromisoformat(value)
                else:
                    # Parse without milliseconds
                    time_obj = dt.time.fromisoformat(value)
                ms_since_midnight = (
                    time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
                ) * 1000 + time_obj.microsecond // 1000
            except ValueError:
                raise ValueError(
                    "Time string must be in format HH:MM:SS or HH:MM:SS.mmm"
                )
        else:
            raise TypeError(f"Unable to convert {type(value)} to Date")

        try:
            self.ptr = getattr(r.RayObject, self.ray_init_method)(ms_since_midnight)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    @property
    def __ms_since_midnight(self) -> int:
        try:
            return getattr(self.ptr, self.ray_extr_method)()
        except TypeError as e:
            raise TypeError(
                f"Expected RayObject type of {self.ray_type_code}, got {self.ptr.get_type()}"
            ) from e

    @property
    def raw_value(self) -> int:
        """Returns raw value of Time object (Milliseconds since midnight)"""
        return self.__ms_since_midnight

    @property
    def value(self) -> dt.time:
        ms = self.__ms_since_midnight
        hours = ms // 3600000
        ms %= 3600000
        minutes = ms // 60000
        ms %= 60000
        seconds = ms // 1000
        milliseconds = ms % 1000
        return dt.time(hours, minutes, seconds, milliseconds * 1000)

    def __str__(self) -> str:
        return self.value.isoformat("milliseconds")

    def __repr__(self) -> str:
        return f"Time({str(self)})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Time):
            return self.value == other.value
        if isinstance(other, dt.time):
            return self.value == other
        if isinstance(other, int):
            return self.raw_value == other
        return False
