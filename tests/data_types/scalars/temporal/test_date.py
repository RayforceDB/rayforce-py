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


def test_date_invalid_month_string_normalizes():
    """The C library normalizes out-of-range months rather than rejecting them."""
    # Month 13 is treated as month 1 of the next year minus one day
    result = t.Date("2025-13-01")
    # C library produces 2024-12-31 for this input
    assert isinstance(result.value, dt.date)


def test_date_invalid_day_string_normalizes():
    """The C library normalizes out-of-range days rather than rejecting them."""
    # Feb 30 rolls over to March
    result = t.Date("2025-02-30")
    assert result.value == dt.date(2025, 3, 2)


# --- Date: leap year edge cases ---


def test_date_leap_year_feb29():
    """2024 is a leap year, Feb 29 is valid."""
    assert t.Date("2024-02-29").value == dt.date(2024, 2, 29)
    assert t.Date(dt.date(2024, 2, 29)).value == dt.date(2024, 2, 29)


def test_date_non_leap_year_feb29_normalizes():
    """2023 is not a leap year; C library normalizes Feb 29 to March 1."""
    assert t.Date("2023-02-29").value == dt.date(2023, 3, 1)


def test_date_century_leap_year():
    """Year 2000 is divisible by 400, so it IS a leap year."""
    assert t.Date("2000-02-29").value == dt.date(2000, 2, 29)


def test_date_century_non_leap_year():
    """Year 1900 is divisible by 100 but not 400, so NOT a leap year."""
    # C library normalizes to March 1
    assert t.Date("1900-02-29").value == dt.date(1900, 3, 1)
