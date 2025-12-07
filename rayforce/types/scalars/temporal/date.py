from __future__ import annotations

import datetime as dt

from rayforce import _rayforce_c as r
from rayforce.core.ffi import FFI
from rayforce.types import exceptions
from rayforce.types.base import Scalar
from rayforce.types.registry import TypeRegistry

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
        if isinstance(value, int):
            return FFI.init_date(value)
        if isinstance(value, str):
            try:
                date_obj = dt.date.fromisoformat(value)
            except ValueError as e:
                raise exceptions.RayInitError(f"Date value is not isoformat: {value}") from e
            return FFI.init_date((date_obj - DATE_EPOCH).days)
        raise exceptions.RayInitError(f"Cannot create Date from {type(value)}")

    def to_python(self) -> dt.date:
        return DATE_EPOCH + dt.timedelta(days=FFI.read_date(self.ptr))

    def to_days(self) -> int:
        return FFI.read_date(self.ptr)


TypeRegistry.register(-r.TYPE_DATE, Date)
