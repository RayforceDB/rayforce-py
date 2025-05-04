import datetime as dt
from typing import Any

from raypy import _rayforce as r
from raypy.types.scalar.date import Date
from raypy.types.scalar.time import Time

EPOCH_DATE = dt.date(1970, 1, 1)


class Timestamp:
    """
    Rayforce Timestamp class
    """

    ptr: r.RayObject

    ray_type_code = r.TYPE_TIMESTAMP
    ray_init_method = "from_timestamp"
    ray_extr_method = "get_timestamp_value"

    def __init__(
        self,
        value: dt.datetime | int | str | None = None,
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

        ms_since_epoch = 0
        if value is None:
            now = dt.datetime.now()
            ms_since_epoch = int(now.timestamp() * 1000)
        elif isinstance(value, int):
            ms_since_epoch = value
        elif isinstance(value, dt.datetime):
            ms_since_epoch = int(value.timestamp() * 1000)
        elif isinstance(value, str):
            # Parse from string (ISO format)
            try:
                dt_obj = dt.datetime.fromisoformat(value)
                ms_since_epoch = int(dt_obj.timestamp() * 1000)
            except ValueError:
                raise ValueError("Timestamp string must be in ISO format")
        else:
            raise TypeError(f"Unable to convert {type(value)} to Date")

        try:
            self.ptr = getattr(r.RayObject, self.ray_init_method)(ms_since_epoch)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    @property
    def __ms_since_epoch(self) -> int:
        try:
            return getattr(self.ptr, self.ray_extr_method)()
        except TypeError as e:
            raise TypeError(
                f"Expected RayObject type of {self.ray_type_code}, got {self.ptr.get_type()}"
            ) from e

    @property
    def raw_value(self) -> int:
        """Returns raw value of Time object (Milliseconds since midnight)"""
        return self.__ms_since_epoch

    @property
    def value(self) -> dt.datetime:
        ms = self.__ms_since_epoch
        seconds = ms // 1000
        microseconds = (ms % 1000) * 1000
        return dt.datetime.fromtimestamp(seconds).replace(microsecond=microseconds)

    @property
    def date(self) -> Date:
        return Date((self.value.date() - EPOCH_DATE).days)

    @property
    def time(self):
        dt = self.value
        return Time(
            ((dt.hour * 60 + dt.minute) * 60 + dt.second) * 1000
            + dt.microsecond // 1000
        )

    def __str__(self) -> str:
        return self.value.isoformat(timespec="milliseconds")

    def __repr__(self) -> str:
        return f"Timestamp({str(self)})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Timestamp):
            return self.value == other.value
        if isinstance(other, dt.datetime):
            return self.value == other
        if isinstance(other, int):
            return self.raw_value == other
        return False
