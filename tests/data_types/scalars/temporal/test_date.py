import datetime as dt

import pytest

from rayforce import types as t


@pytest.mark.parametrize(
    "input_val,expected",
    [
        (dt.date(2025, 5, 10), dt.date(2025, 5, 10)),
        ("2025-05-10", dt.date(2025, 5, 10)),
    ],
)
def test_date(input_val, expected):
    assert t.Date(input_val).value == expected


# --- Date: invalid date string parsing ---


def test_date_invalid_string_raises():
    with pytest.raises(RuntimeError):
        t.Date("not-a-date")


def test_date_invalid_month_string_raises():
    """The C library rejects out-of-range months rather than normalizing them."""
    with pytest.raises(RuntimeError):
        t.Date("2025-13-01")


def test_date_invalid_day_string_raises():
    """The C library rejects out-of-range days rather than normalizing them."""
    with pytest.raises(RuntimeError):
        t.Date("2025-02-30")


# --- Date: leap year edge cases ---


def test_date_leap_year_feb29():
    """2024 is a leap year, Feb 29 is valid."""
    assert t.Date("2024-02-29").value == dt.date(2024, 2, 29)
    assert t.Date(dt.date(2024, 2, 29)).value == dt.date(2024, 2, 29)


def test_date_non_leap_year_feb29_raises():
    """2023 is not a leap year; C library rejects Feb 29."""
    with pytest.raises(RuntimeError):
        t.Date("2023-02-29")


def test_date_century_leap_year():
    """Year 2000 is divisible by 400, so it IS a leap year."""
    assert t.Date("2000-02-29").value == dt.date(2000, 2, 29)


def test_date_century_non_leap_year():
    """Year 1900 is divisible by 100 but not 400, so NOT a leap year."""
    with pytest.raises(RuntimeError):
        t.Date("1900-02-29")


def test_date_from_int_days():
    """Construct from the raw day offset since the 2000-01-01 epoch."""
    assert t.Date(0).value == dt.date(2000, 1, 1)
    assert t.Date(9261).value == dt.date(2025, 5, 10)
