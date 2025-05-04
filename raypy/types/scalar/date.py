import datetime as dt
from typing import Any

from raypy import _rayforce as r

EPOCH_DATE = dt.date(1970, 1, 1)


class Date:
    """
    Rayforce Date class
    """

    ptr: r.RayObject

    ray_type_code = r.TYPE_DATE
    ray_init_method = "from_date"
    ray_extr_method = "get_date_value"

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
            self.ptr = getattr(r.RayObject, self.ray_init_method)(days_since_epoch)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    @property
    def __days_since_epoch(self) -> int:
        try:
            return getattr(self.ptr, self.ray_extr_method)()
        except TypeError as e:
            raise TypeError(
                f"Expected RayObject type of {self.ray_type_code}, got {self.ptr.get_type()}"
            ) from e

    @property
    def raw_value(self) -> int:
        """Returns raw value of Date object (Number of days since Epoch)"""
        return self.__days_since_epoch

    @property
    def value(self) -> dt.date:
        return EPOCH_DATE + dt.timedelta(days=self.__days_since_epoch)

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
