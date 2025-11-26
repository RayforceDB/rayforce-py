from __future__ import annotations
import numpy as np
import datetime as dt

from raypy import _rayforce as r
from raypy.core.ffi import FFI
from raypy.types.base import Scalar
from raypy.types.registry import TypeRegistry
from raypy.types import exceptions

epoch2000 = np.datetime64("2000-01-01T00:00:00", "ns")
epoch2000_py = dt.datetime(2000, 1, 1, tzinfo=dt.timezone.utc)


class Timestamp(Scalar):
    """
    Represents a point in time with millisecond precision.
    """

    type_code = -r.TYPE_TIMESTAMP
    ray_name = "Timestamp"

    def _create_from_value(self, value: dt.datetime | int | str) -> r.RayObject:
        if isinstance(value, dt.datetime):
            # Compute nanoseconds since 2000-01-01
            delta = value - epoch2000_py
            ns = (
                delta.days * 24 * 3600 * 1_000_000_000
                + delta.seconds * 1_000_000_000
                + delta.microseconds * 1_000
            )
            return FFI.init_timestamp(ns)

        elif isinstance(value, int):
            # assume already nanoseconds since 2000-01-01
            return FFI.init_timestamp(value)

        elif isinstance(value, str):
            # Parse ISO format string
            dt_obj = dt.datetime.fromisoformat(value)
            delta = dt_obj - epoch2000_py
            ns = (
                delta.days * 24 * 3600 * 1_000_000_000
                + delta.seconds * 1_000_000_000
                + delta.microseconds * 1_000
            )
            return FFI.init_timestamp(ns)

        else:
            raise exceptions.RayInitException(
                f"Cannot create Timestamp from {type(value)}"
            )

    def to_python(self) -> np.datetime64:
        nano = FFI.read_timestamp(self.ptr)
        return epoch2000 + np.timedelta64(nano, "ns")

    def dt(self) -> dt.datetime:
        return self.to_python().astype("datetime64[us]").astype(dt.datetime)

    def to_millis(self) -> int:
        return FFI.read_timestamp(self.ptr)


TypeRegistry.register(-r.TYPE_TIMESTAMP, Timestamp)
