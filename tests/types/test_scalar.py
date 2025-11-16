import uuid
import datetime as dt
import pytest

from raypy import types as t


def test_guid():
    u_id = uuid.uuid4()
    assert t.GUID(str(u_id)).value == u_id


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
    assert t.B8(value).value == expected_value


def test_c8():
    assert t.C8("1").value == "1"
    assert t.C8("A").value == "A"

    with pytest.raises(t.RayInitException):
        t.C8("123")


def test_date():
    d = dt.date(year=2025, month=5, day=10)
    assert t.Date(d).value == d
    assert t.Date(9261).value == d
    assert t.Date("2025-05-10").value == d

    with pytest.raises(t.RayInitException):
        t.Date("wrong-format")


def test_f64():
    assert t.F64(123).value == 123.0
    assert t.F64(123.0).value == 123.0

    with pytest.raises(t.RayInitException):
        t.C8("123")


def test_integers():
    assert t.I16(123).value == 123
    assert t.I32(123).value == 123
    assert t.I64(123).value == 123

    with pytest.raises(t.RayInitException):
        t.C8("wrong-format")


def test_symbol():
    assert t.Symbol("Test").value == "Test"
    assert t.Symbol("123").value == "123"


def test_time():
    tt = dt.time(hour=10, minute=15, second=20)
    assert t.Time(36920000).value == tt
    assert t.Time(tt).value == tt
    assert t.Time("10:15:20").value == tt

    with pytest.raises(t.RayInitException):
        t.Time("wrong-format")


def test_u8():
    assert t.U8(1).value == 1

    with pytest.raises(t.RayInitException):
        t.U8(256)

    with pytest.raises(t.RayInitException):
        t.U8(-1)
