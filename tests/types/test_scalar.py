import datetime as dt
import pytest

from raypy.api import exceptions
from raypy.types import scalar as s


@pytest.mark.parametrize(
    "value, expected_value",
    [
        (True, True),
        (False, False),
        (0, False),
        (1, True),
        ("True", True),
        ("False", True),
    ],
)
def test_b8(value, expected_value):
    assert s.B8(value).value == expected_value


def test_c8():
    assert s.C8("1").value == "1"
    assert s.C8("A").value == "A"

    with pytest.raises(exceptions.CAPIError):
        s.C8("123")

def test_date():
    d = dt.date(year=2025, month=5, day=10)
    assert s.Date(d).value == d
    assert s.Date(20218).value == d
    assert s.Date("2025-05-10").value == d

    with pytest.raises(ValueError):
        s.Date("wrong-format")


def test_f64():
    assert s.F64(123).value == 123.0
    assert s.F64(123.0).value == 123.0

    with pytest.raises(exceptions.CAPIError):
        s.C8("123")


def test_integers():
    assert s.I16(123).value == 123
    assert s.I32(123).value == 123
    assert s.I64(123).value == 123

    with pytest.raises(exceptions.CAPIError):
        s.C8("wrong-format")


def test_symbol():
    assert s.Symbol("Test").value == "Test"
    assert s.Symbol("123").value == "123"


def test_time():
    t = dt.time(hour=10, minute=15, second=20)
    assert s.Time(36920000).value == t
    assert s.Time(t).value == t
    assert s.Time("10:15:20").value == t

    with pytest.raises(ValueError):
        s.Time("wrong-format")

def test_timestamp():
    t = dt.datetime(year=2025, month=10, day=5, hour=10, minute=15, second=20)
    assert s.Timestamp(t).value == t
    assert s.Timestamp(1759655720000).value == t
    assert s.Timestamp(t.isoformat()).value == t

    with pytest.raises(ValueError):
        s.Timestamp("wrong-format")

def test_u8():
    assert s.U8(1).value == 1

    with pytest.raises(ValueError):
        s.U8(256)

    with pytest.raises(ValueError):
        s.U8(-1)
