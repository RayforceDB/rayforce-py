import uuid
import datetime as dt
import typing as t

from raypy import api
from raypy import _rayforce as r

DATE_COUNTS_FROM = dt.date(2000, 1, 1)


class __RaypyScalar:
    """
    This class is an abstract object for all scalar types.

    Should not be used directly.
    """

    ptr: r.RayObject

    type_code: int

    def __init__(
        self,
        value: t.Any | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        if value is None and ptr is None:
            raise ValueError(
                f"{self.__class__.__name__} class requires at least one initialization argument."
            )

        if self.type_code is None:
            raise AttributeError(f"{self.__name__} type code is not set")

        if ptr is not None:
            if (
                not isinstance(ptr, r.RayObject)
                or (type_code := ptr.get_obj_type()) != self.type_code
            ):
                raise ValueError(
                    f"Expected RayObject of type {self.type_code} for {self.__class__.__name__}, got {type_code}",
                )

            self.ptr = ptr

    @property
    def value(self) -> t.Any:
        raise NotImplementedError

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    def __repr__(self) -> str:
        return self.__str__()


class B8(__RaypyScalar):
    """
    Rayforce boolean type.

    Type code: -1
    """

    type_code = -r.TYPE_B8

    def __init__(
        self,
        value: t.Any | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ptr=ptr)

        if not getattr(self, "ptr", None):
            self.ptr = api.init_b8(value)

    @property
    def value(self) -> bool:
        return api.read_b8(self.ptr)

    def __bool__(self) -> bool:
        return self.value

    def __eq__(self, eq: t.Any) -> bool:
        if isinstance(eq, B8):
            return self.value == eq.value
        return False


class C8(__RaypyScalar):
    """
    Rayforce char type.

    Type code: -12
    """

    type_code = -r.TYPE_C8

    def __init__(
        self,
        value: str | int | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ptr=ptr)

        if not getattr(self, "ptr", None):
            try:
                _value = str(value)
            except ValueError as e:
                raise ValueError(f"{value} can not be represented as C8") from e
            print(_value)
            if len(_value) != 1:
                raise ValueError(f"{value} can not be represented as C8")

            self.ptr = api.init_c8(_value)

    @property
    def value(self) -> str:
        return api.read_c8(self.ptr)

    def __eq__(self, eq: t.Any) -> bool:
        if isinstance(eq, C8):
            return self.value == eq.value
        return False


class Date(__RaypyScalar):
    """
    Rayforce date class.

    Type code: -7
    """

    type_code = -r.TYPE_DATE

    def __init__(
        self,
        value: dt.date | int | str | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ptr=ptr)

        if not getattr(self, "ptr", None):
            if isinstance(value, int):
                days_since_epoch = value
            elif isinstance(value, dt.date):
                days_since_epoch = (value - DATE_COUNTS_FROM).days
            elif isinstance(value, str):
                try:
                    date_obj = dt.date.fromisoformat(value)
                    days_since_epoch = (date_obj - DATE_COUNTS_FROM).days
                except ValueError as e:
                    raise ValueError("Date string must be in format YYYY-MM-DD") from e

            self.ptr = api.init_date(days_since_epoch)

    @property
    def value(self) -> dt.date:
        days_since_epoch = api.read_date(self.ptr)
        return DATE_COUNTS_FROM + dt.timedelta(days=days_since_epoch)


class F64(__RaypyScalar):
    """
    Rayforce float class.

    Type code: -10
    """

    type_code = -r.TYPE_F64

    def __init__(
        self,
        value: int | float | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ptr=ptr)

        if not getattr(self, "ptr", None) and value is not None:
            try:
                _value = float(value)
            except ValueError as e:
                raise ValueError(f"{value} can not be represented as F64") from e

            self.ptr = api.init_f64(_value)

    @property
    def value(self) -> float:
        return api.read_f64(self.ptr)

    def __eq__(self, eq: t.Any) -> bool:
        if isinstance(eq, F64):
            return self.value == eq.value
        return False


class I16(__RaypyScalar):
    """
    Rayforce 16-bit integer. Analog of Python int (-32768 to 32767).

    Type code: -3
    """

    type_code = -r.TYPE_I16

    def __init__(
        self,
        value: int | float | str | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ptr=ptr)

        if not getattr(self, "ptr", None) and value is not None:
            try:
                _value = int(value)
            except ValueError as e:
                raise ValueError(f"{value} can not be represented as I16") from e

            if _value < -32767 or _value > 32767:
                raise ValueError("I16 is out of range (-32767 to 32767)")

            self.ptr = api.init_i16(_value)

    @property
    def value(self) -> int:
        return api.read_i16(self.ptr)

    def __eq__(self, eq: t.Any) -> bool:
        if isinstance(eq, (I64, I16, I32)):
            return self.value == eq.value
        return False


class I32(__RaypyScalar):
    """
    Rayforce 32-bit integer. Analog of Python int (-2147483648 to 2147483647)

    Type code: -4
    """

    type_code = -r.TYPE_I32

    def __init__(
        self,
        value: int | float | str | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ptr=ptr)

        if not getattr(self, "ptr", None) and value is not None:
            try:
                _value = int(value)
            except ValueError as e:
                raise ValueError(f"{value} can not be represented as I32") from e

            if _value < -2147483648 or _value > 2147483647:
                raise ValueError("I32 is out of range (-2147483648 to 2147483647)")

            self.ptr = api.init_i32(_value)

    @property
    def value(self) -> int:
        return api.read_i32(self.ptr)

    def __eq__(self, eq: t.Any) -> bool:
        if isinstance(eq, (I64, I16, I32)):
            return self.value == eq.value
        return False


class I64(__RaypyScalar):
    """
    Rayforce 64-bit integer. Analog of Python int

    Type code: -5
    """

    type_code = -r.TYPE_I64

    def __init__(
        self,
        value: int | float | str | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ptr=ptr)

        if not getattr(self, "ptr", None) and value is not None:
            try:
                _value = int(value)
            except ValueError as e:
                raise ValueError(f"{value} can not be represented as I64") from e

            if _value < -9223372036854775808 or _value > 9223372036854775808:
                raise ValueError("I64 is out of range")

            self.ptr = api.init_i64(_value)

    @property
    def value(self) -> int:
        return api.read_i64(self.ptr)

    def __eq__(self, eq: t.Any) -> bool:
        if isinstance(eq, (I64, I16, I32)):
            return self.value == eq.value
        return False

    def __str__(self) -> str:
        if self.value == -9223372036854775808:
            return ""
        return super().__str__()


class Symbol(__RaypyScalar):
    """
    Rayforce symbol type.

    Type code: -6
    """

    type_code = -r.TYPE_SYMBOL

    def __init__(
        self,
        value: str | t.Any | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ptr=ptr)

        try:
            _value = str(value)
        except ValueError as e:
            raise ValueError(f"{value} can not be represented as Symbol") from e

        if not getattr(self, "ptr", None):
            self.ptr = api.init_symbol(_value)

    @property
    def value(self) -> str:
        return api.read_symbol(self.ptr)

    def __eq__(self, eq: t.Any) -> bool:
        if isinstance(eq, Symbol):
            return self.value == eq.value
        return False


class Time(__RaypyScalar):
    """
    Rayforce time type.

    Type code: -8
    """

    type_code = -r.TYPE_TIME

    def __init__(
        self,
        value: dt.time | int | str | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ptr=ptr)

        if not getattr(self, "ptr", None):
            if isinstance(value, int):
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

            self.ptr = api.init_time(ms_since_midnight)

    @property
    def value(self) -> dt.time:
        ms_since_midnight = api.read_time(self.ptr)

        hours = ms_since_midnight // 3600000
        ms_since_midnight %= 3600000

        minutes = ms_since_midnight // 60000
        ms_since_midnight %= 60000

        seconds = ms_since_midnight // 1000
        milliseconds = ms_since_midnight % 1000

        return dt.time(hours, minutes, seconds, milliseconds * 1000)

    def __eq__(self, eq: t.Any) -> bool:
        if isinstance(eq, Time):
            return self.value == eq.value
        return False


class Timestamp(__RaypyScalar):
    """
    Rayforce timestamp type.

    Type code: -9
    """

    type_code = -r.TYPE_TIMESTAMP

    def __init__(
        self,
        value: dt.datetime | int | str | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ptr=ptr)

        if not getattr(self, "ptr", None):
            ms_since_epoch = 0
            if isinstance(value, int):
                ms_since_epoch = value
            elif isinstance(value, dt.datetime):
                ms_since_epoch = int(value.timestamp() * 1000)
            elif isinstance(value, str):  # Parse from string (ISO format)
                try:
                    dt_obj = dt.datetime.fromisoformat(value)
                    ms_since_epoch = int(dt_obj.timestamp() * 1000)
                except ValueError:
                    raise ValueError("Timestamp string must be in ISO format")

            self.ptr = api.init_timestamp(ms_since_epoch)

    @property
    def value(self) -> dt.datetime:
        ms_since_epoch = api.read_timestamp(self.ptr)
        seconds = ms_since_epoch // 1000
        microseconds = (ms_since_epoch % 1000) * 1000
        return dt.datetime.fromtimestamp(seconds).replace(microsecond=microseconds)

    def __eq__(self, eq: t.Any) -> bool:
        if isinstance(eq, Timestamp):
            return self.value == eq.value
        return False


class U8(__RaypyScalar):
    """
    Rayforce unsigned type.

    Type code: -2
    """

    type_code = -r.TYPE_U8

    def __init__(
        self,
        value: int | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ptr=ptr)

        if not getattr(self, "ptr", None):
            if value is not None and (value < 0 or value > 255):
                raise ValueError("Unsigned value is out of range (0-255)")

            self.ptr = api.init_u8(value)

    @property
    def value(self) -> int:
        return api.read_u8(self.ptr)

    def __eq__(self, eq: t.Any) -> bool:
        if isinstance(eq, U8):
            return self.value == eq.value
        return False


class GUID(__RaypyScalar):
    """
    Rayforce GUID type (Globally unique identifier)

    Type code: -11
    """

    type_code = -r.TYPE_GUID

    def __init__(
        self,
        value: str | uuid.UUID | bytes | bytearray | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ptr=ptr)

        if not getattr(self, "ptr", None):
            if isinstance(value, uuid.UUID):
                guid = str(value)
            elif isinstance(value, str):
                guid = value
            elif isinstance(value, (bytes, bytearray)):
                guid = str(uuid.UUID(bytes=value))

            self.ptr = api.init_guid(guid)

    @property
    def value(self) -> str:
        guid_bytes = api.read_guid(self.ptr)
        return str(uuid.UUID(bytes=guid_bytes))

    def __str__(self) -> str:
        return f"GUID({self.value})"


type ScalarType = (
    I16 | I32 | I64 | F64 | B8 | C8 | Date | Symbol | Time | Timestamp | U8 | GUID
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
    "GUID",
    "ScalarType",
]
