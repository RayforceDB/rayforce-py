import datetime as dt
from typing import Any

from raypy import _rayforce as r
from raypy.types.scalar.date import Date
from raypy.types.scalar.time import Time

EPOCH_DATE = dt.date(1970, 1, 1)


class Timestamp:
    """
    # Rayforce Timestamp type
    Analog of Python datetime.datetime

    ### Init Arguments:
        `value`: dt.time | int | str | None - Python datetime.datetime or
            int represents MS since EPOCH (1970.1.1) or datetime in str isoformat
        `ray_obj`: rayforce.RayObject | None - RayObject pointer instance
    """

    ptr: r.RayObject

    # This class represents scalar value, hence code is negative
    ray_type_code = -r.TYPE_TIMESTAMP

    ray_init_method = "init_timestamp"
    ray_extr_method = "read_timestamp"

    def __init__(
        self,
        value: dt.datetime | int | str | None = None,
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

        ms_since_epoch = 0
        if value is None:
            now = dt.datetime.now()
            ms_since_epoch = int(now.timestamp() * 1000)
        elif isinstance(value, int):
            ms_since_epoch = value
        elif isinstance(value, dt.datetime):
            ms_since_epoch = int(value.timestamp() * 1000)
        elif isinstance(value, str):  # Parse from string (ISO format)
            try:
                dt_obj = dt.datetime.fromisoformat(value)
                ms_since_epoch = int(dt_obj.timestamp() * 1000)
            except ValueError:
                raise ValueError("Timestamp string must be in ISO format")
        else:
            raise TypeError(f"Unable to convert {type(value)} to Date")

        try:
            self.ptr = getattr(r, self.ray_init_method)(ms_since_epoch)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    @property
    def ms_since_epoch(self) -> int:
        try:
            return getattr(r, self.ray_extr_method)(self.ptr)
        except Exception as e:
            raise TypeError(f"Error during timestamp type extraction - {str(e)}") from e

    @property
    def value(self) -> dt.datetime:
        ms = self.ms_since_epoch
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
            return self.ms_since_epoch == other
        return False
