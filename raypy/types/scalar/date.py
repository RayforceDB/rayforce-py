import datetime as dt
from typing import Any

from raypy import _rayforce as r

EPOCH_DATE = dt.date(1970, 1, 1)


class Date:
    """
    ## Rayforce Date class.
    Analog of datetime.date in Python

    ### Init Arguments:
        `value`: dt.date | int | str | None - Datetime date object, or days since Epoch,
            or string isoformat representation of a date. Leave as None to have today's date
        `ray_obj`: rayforce.RayObject | None - RayObject pointer instance
    """

    ptr: r.RayObject

    # This class represents scalar value, hence code is negative
    ray_type_code = -r.TYPE_DATE

    ray_init_method = "init_date"
    ray_extr_method = "read_date"

    def __init__(
        self,
        value: dt.date | int | str | None = None,
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

        days_since_epoch = 0
        if value is None:
            days_since_epoch = (dt.date.today() - EPOCH_DATE).days
        elif isinstance(value, int):
            days_since_epoch = value
        elif isinstance(value, dt.date):
            days_since_epoch = (value - EPOCH_DATE).days
        elif isinstance(value, str):
            try:
                date_obj = dt.date.fromisoformat(value)
                days_since_epoch = (date_obj - EPOCH_DATE).days
            except ValueError as e:
                raise ValueError("Date string must be in format YYYY-MM-DD") from e
        else:
            raise TypeError(f"Unable to convert {type(value)} to Date")

        try:
            self.ptr = getattr(r, self.ray_init_method)(days_since_epoch)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    @property
    def raw_value(self) -> int:
        """Returns an integer which represents a number of days since epoch"""
        try:
            return getattr(r, self.ray_extr_method)(self.ptr)
        except Exception as e:
            raise ValueError(f"Error during Date type extraction - {str(e)}")

    @property
    def value(self) -> dt.date:
        return EPOCH_DATE + dt.timedelta(days=self.raw_value)

    def __str__(self) -> str:
        return self.value.isoformat()

    def __repr__(self) -> str:
        return f"Date({str(self)})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Date):
            return self.value == other.value
        if isinstance(other, dt.date):
            return self.value == other
        if isinstance(other, int):
            return self.raw_value == other
        return False
