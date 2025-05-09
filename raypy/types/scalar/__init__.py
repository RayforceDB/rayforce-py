from .integer import i16, i32, i64
from .float import f64
from .bool import b8
from .date import Date
from .time import Time
from .timestamp import Timestamp
from .unsigned import u8
from .char import c8
from .symbol import Symbol


type ScalarType = (
    Symbol | i16 | i32 | i64 | f64 | b8 | Date | Time | Timestamp | u8 | c8
)


__all__ = [
    "i16",
    "i32",
    "i64",
    "f64",
    "b8",
    "Date",
    "Time",
    "Timestamp",
    "u8",
    "c8",
    "Symbol",
]
