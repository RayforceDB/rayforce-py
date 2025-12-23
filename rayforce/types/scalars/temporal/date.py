from __future__ import annotations

import datetime as dt

from rayforce import _rayforce_c as r
from rayforce.ffi import FFI
from rayforce.types.base import Scalar
from rayforce.types.registry import TypeRegistry

# Date counts from this epoch
DATE_EPOCH = dt.date(2000, 1, 1)


class Date(Scalar):
    """
    Represents date as days since 2000-01-01.
    """

    type_code = -r.TYPE_DATE
    ray_name = "date"

    def _create_from_value(self, value: dt.date | int | str) -> r.RayObject:
        return FFI.init_date(value)

    def to_python(self) -> dt.date:
        return DATE_EPOCH + dt.timedelta(days=FFI.read_date(self.ptr))

    def to_days(self) -> int:
        return FFI.read_date(self.ptr)


TypeRegistry.register(-r.TYPE_DATE, Date)
