import datetime as dt
from typing import Any

from raypy import api
from raypy.types import common
from raypy import _rayforce as r

EPOCH_DATE = dt.date(1970, 1, 1)


class B8(common.RaypyScalar):
    """
    Rayforce boolean type.
    """

    _type = -r.TYPE_B8

    def __init__(
        self,
        value: Any | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ray_obj=ray_obj)

        if not getattr(self, "ptr", None):
            self.ptr = api.init_b8(value)

    @property
    def value(self) -> bool:
        return api.read_b8(self.ptr)

    def __bool__(self) -> bool:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"b8({self.value})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, B8):
            return self.value == other.value
        if isinstance(other, bool):
            return self.value == other
        return False


class C8(common.RaypyScalar):
    """
    Rayforce char type
    """

    _type = -r.TYPE_C8

    def __init__(
        self,
        value: str | int | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ray_obj=ray_obj)

        if not getattr(self, "ptr", None):
            self.ptr = api.init_c8(value)

    @property
    def value(self) -> str:
        return api.read_c8(self.ptr)

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"c8({self.value})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, C8):
            return self.value == other.value
        if isinstance(other, str) and len(other) == 1:
            return self.value == other
        return False


class Date(common.RaypyScalar):
    """
    Rayforce date class
    """

    _type = -r.TYPE_DATE

    def __init__(
        self,
        value: dt.date | int | str | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ray_obj=ray_obj)

        if not getattr(self, "ptr", None):
            self.ptr = api.init_date(value)

    @property
    def value(self) -> dt.date:
        return api.read_date(self.ptr)

    def __str__(self) -> str:
        return self.value.isoformat()

    def __repr__(self) -> str:
        return f"Date({str(self)})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Date):
            return self.value == other.value
        if isinstance(other, dt.date):
            return self.value == other
        return False


class F64(common.RaypyScalar):
    """
    Rayforce float class
    """

    _type = -r.TYPE_F64

    def __init__(
        self,
        value: int | float | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ray_obj=ray_obj)

        if not getattr(self, "ptr", None):
            self.ptr = api.init_f64(value)

    @property
    def value(self) -> float:
        return api.read_f64(self.ptr)

    def __float__(self) -> float:
        return float(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"f64({self.value})"

    def __eq__(self, other: Any):
        if isinstance(other, F64):
            return self.value == other.value
        return self.value == other


class __RayInteger(common.RaypyScalar):
    """
    Base class for Rayforce integers (i16, i32, i64)
    """

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, __RayInteger):
            return self.value == other.value
        return self.value == other

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, __RayInteger):
            return self.value < other.value
        return self.value < other

    def __le__(self, other: Any) -> bool:
        if isinstance(other, __RayInteger):
            return self.value <= other.value
        return self.value <= other

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, __RayInteger):
            return self.value > other.value
        return self.value > other

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, __RayInteger):
            return self.value >= other.value
        return self.value >= other


class I16(__RayInteger):
    """
    Rayforce 16-bit integer. Analog of Python int (-32768 to 32767)
    """

    _type = -r.TYPE_I16

    def __init__(
        self,
        value: int | float | str | None = None,
        *,
        ray_obj: Any | None = None,
    ) -> None:
        super().__init__(value, ray_obj=ray_obj)

        if not getattr(self, "ptr", None):
            self.ptr = api.init_i16(value)

    @property
    def value(self) -> int:
        return api.read_i16(self.ptr)


class I32(__RayInteger):
    """
    Rayforce 32-bit integer. Analog of Python int (-2147483648 to 2147483647)
    """

    _type = -r.TYPE_I32

    def __init__(
        self,
        value: int | float | str | None = None,
        *,
        ray_obj: Any | None = None,
    ) -> None:
        super().__init__(value, ray_obj=ray_obj)

        if not getattr(self, "ptr", None):
            self.ptr = api.init_i32(value)

    @property
    def value(self) -> int:
        return api.read_i32(self.ptr)


class I64(__RayInteger):
    """
    Rayforce 64-bit integer. Analog of Python int
    """

    _type = -r.TYPE_I64

    def __init__(
        self,
        value: int | float | str | None = None,
        *,
        ray_obj: Any | None = None,
    ) -> None:
        super().__init__(value, ray_obj=ray_obj)

        if not getattr(self, "ptr", None):
            self.ptr = api.init_i64(value)

    @property
    def value(self) -> int:
        return api.read_i64(self.ptr)


class Symbol(common.RaypyScalar):
    """
    Rayforce Symbol type
    """

    _type = -r.TYPE_SYMBOL

    def __init__(
        self,
        value: str | Any | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ray_obj=ray_obj)

        if not getattr(self, "ptr", None):
            self.ptr = api.init_symbol(value)

    @property
    def value(self) -> str:
        return api.read_symbol(self.ptr)

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Symbol({self.value})"

    def __eq__(self, other: Any) -> bool:
        """Equality comparison."""
        if isinstance(other, Symbol):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return False

    def __hash__(self):
        return hash(self.value)

    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)


class Time(common.RaypyScalar):
    """
    Rayforce Time type
    """

    _type = -r.TYPE_TIME

    def __init__(
        self,
        value: dt.time | int | str | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ray_obj=ray_obj)

        if not getattr(self, "ptr", None):
            self.ptr = api.init_time(value)

    @property
    def value(self) -> dt.time:
        return api.read_time(self.ptr)

    def __str__(self) -> str:
        return self.value.isoformat("milliseconds")

    def __repr__(self) -> str:
        return f"Time({str(self)})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Time):
            return self.value == other.value
        if isinstance(other, dt.time):
            return self.value == other
        return False


class Timestamp(common.RaypyScalar):
    """
    Rayforce Timestamp type
    """

    _type = -r.TYPE_TIMESTAMP

    def __init__(
        self,
        value: dt.datetime | int | str | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ray_obj=ray_obj)

        if not getattr(self, "ptr", None):
            self.ptr = api.init_timestamp(value)

    @property
    def value(self) -> dt.datetime:
        return api.read_timestamp(self.ptr)

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
        return False


class U8(common.RaypyScalar):
    """
    Rayforce Unsigned type
    """

    _type = -r.TYPE_U8

    def __init__(
        self,
        value: int | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ray_obj=ray_obj)

        if not getattr(self, "ptr", None):
            self.ptr = api.init_U8(value)

    @property
    def value(self) -> int:
        return api.read_U8(self.ptr)

    def __int__(self) -> int:
        return self.value

    def __index__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"U8({self.value})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, U8):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        return False

    def __add__(self, other: Any) -> "U8":
        if isinstance(other, U8):
            other = other.value
        result = self.value + other
        # Wrap around on overflow
        result = result & 0xFF
        return U8(result)

    def __sub__(self, other: Any) -> "U8":
        if isinstance(other, U8):
            other = other.value
        result = self.value - other
        # Wrap around on underflow
        result = result & 0xFF
        return U8(result)

    def __mul__(self, other: Any) -> "U8":
        if isinstance(other, U8):
            other = other.value
        result = self.value * other
        # Wrap around on overflow
        result = result & 0xFF
        return U8(result)

    def __floordiv__(self, other: Any) -> "U8":
        if isinstance(other, U8):
            other = other.value
        if other == 0:
            raise ZeroDivisionError("division by zero")
        result = self.value // other
        return U8(result)

    def __mod__(self, other: Any) -> "U8":
        if isinstance(other, U8):
            other = other.value
        if other == 0:
            raise ZeroDivisionError("modulo by zero")
        result = self.value % other
        return U8(result)


type ScalarType = (
    I16 | I32 | I64 | F64 | B8 | C8 | Date | Symbol | Time | Timestamp | U8
)

__all__ = [
    "I16",
    "I32",
    "I64",
    "F64",
    "B8",
    "C8",
    "Date",
    "Symbol",
    "Time",
    "Timestamp",
    "U8",
    "ScalarType",
]
