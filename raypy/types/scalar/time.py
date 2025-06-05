import datetime as dt
from typing import Any

from raypy import _rayforce as r


class Time:
    """
    # Rayforce Time type
    Analog of Python datetime.time

    ### Init Arguments:
        `value`: dt.time | int | str | None - Python datetime.time or
            int represents MS since midnight or time in str isoformat (HH:MM:SS or HH:MM:SS.mmm)
        `ray_obj`: rayforce.RayObject | None - RayObject pointer instance
    """

    ptr: r.RayObject

    # This class represents scalar value, hence code is negative
    ray_type_code = -r.TYPE_TIME

    ray_init_method = "init_time"
    ray_extr_method = "read_time"

    def __init__(
        self,
        value: dt.time | int | str | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if ray_obj is not None:
            if (_type := ray_obj.get_obj_type()) != self.ray_type_code:
                raise ValueError(
                    f"Expected RayObject of type {self.ray_type_code}, got {_type}"
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
                raise ValueError(
                    "Time int value must be in range 0-86399999 milliseconds"
                )
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
            except ValueError as e:
                raise ValueError(
                    "Time string must be in format HH:MM:SS or HH:MM:SS.mmm"
                ) from e
        else:
            raise TypeError(f"Unable to convert {type(value)} to Time")

        try:
            self.ptr = getattr(r, self.ray_init_method)(ms_since_midnight)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    @property
    def ms_since_midnight(self) -> int:
        try:
            return getattr(r, self.ray_extr_method)(self.ptr)
        except Exception as e:
            raise TypeError(f"Error during time type extraction - {str(e)}") from e

    @property
    def value(self) -> dt.time:
        ms = self.ms_since_midnight
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
            return self.ms_since_midnight == other
        return False
