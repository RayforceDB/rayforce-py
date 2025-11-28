from __future__ import annotations
import datetime as dt

from raypy import _rayforce_c as r
from raypy.core.ffi import FFI
from raypy.types.base import Scalar
from raypy.types.registry import TypeRegistry
from raypy.types import exceptions

# Date counts from this epoch
DATE_EPOCH = dt.date(2000, 1, 1)


class Date(Scalar):
    """
    Represents date as days since 2000-01-01.
    """

    type_code = -r.TYPE_DATE
    ray_name = "Date"

    def _create_from_value(self, value: dt.date | int | str) -> r.RayObject:
        if isinstance(value, dt.date):
            days_since_epoch = (value - DATE_EPOCH).days
            return FFI.init_date(days_since_epoch)
        elif isinstance(value, int):
            return FFI.init_date(value)
        elif isinstance(value, str):
            # Parse ISO format
            try:
                date_obj = dt.date.fromisoformat(value)
            except ValueError as e:
                raise exceptions.RayInitException from e
            days_since_epoch = (date_obj - DATE_EPOCH).days
            return FFI.init_date(days_since_epoch)
        else:
            raise exceptions.RayInitException(f"Cannot create Date from {type(value)}")

    def to_python(self) -> dt.date:
        days = FFI.read_date(self.ptr)
        return DATE_EPOCH + dt.timedelta(days=days)

    def to_days(self) -> int:
        return FFI.read_date(self.ptr)


TypeRegistry.register(-r.TYPE_DATE, Date)
