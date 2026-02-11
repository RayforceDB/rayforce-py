import datetime as dt

import pytest

from rayforce import types as t


@pytest.mark.parametrize(
    "attr,expected",
    [
        ("year", 2025),
        ("month", 5),
        ("day", 10),
        ("hour", 14),
        ("minute", 30),
        ("second", 45),
    ],
)
def test_timestamp(attr, expected):
    dt_obj = dt.datetime(2025, 5, 10, 14, 30, 45, tzinfo=dt.UTC)
    result = t.Timestamp(dt_obj)
    assert getattr(result.value, attr) == expected


# --- Timestamp: timezone handling ---


def test_timestamp_utc():
    ts = dt.datetime(2025, 6, 15, 12, 30, 0, tzinfo=dt.UTC)
    result = t.Timestamp(ts)
    assert result.value == dt.datetime(2025, 6, 15, 12, 30, 0, tzinfo=dt.UTC)


def test_timestamp_positive_tz_offset_normalizes_to_utc():
    """A +5h offset datetime should normalize to the same UTC instant."""
    tz_plus5 = dt.timezone(dt.timedelta(hours=5))
    ts = dt.datetime(2025, 6, 15, 17, 30, 0, tzinfo=tz_plus5)
    result = t.Timestamp(ts)
    expected = dt.datetime(2025, 6, 15, 12, 30, 0, tzinfo=dt.UTC)
    assert result.value == expected


def test_timestamp_negative_tz_offset_normalizes_to_utc():
    """A -5h offset datetime should normalize to the same UTC instant."""
    tz_minus5 = dt.timezone(dt.timedelta(hours=-5))
    ts = dt.datetime(2025, 6, 15, 7, 30, 0, tzinfo=tz_minus5)
    result = t.Timestamp(ts)
    expected = dt.datetime(2025, 6, 15, 12, 30, 0, tzinfo=dt.UTC)
    assert result.value == expected


def test_timestamp_naive_datetime():
    """Naive (no timezone) datetime is treated as UTC."""
    ts = dt.datetime(2025, 6, 15, 12, 30, 0)
    result = t.Timestamp(ts)
    assert result.value == dt.datetime(2025, 6, 15, 12, 30, 0, tzinfo=dt.UTC)


# --- Timestamp: string parsing ---


@pytest.mark.parametrize(
    "input_str",
    [
        "2025-06-15T12:30:00",
        "2025-06-15T12:30:00Z",
        "2025-06-15 12:30:00",
    ],
)
def test_timestamp_string_parsing(input_str):
    result = t.Timestamp(input_str)
    assert result.value == dt.datetime(2025, 6, 15, 12, 30, 0, tzinfo=dt.UTC)


# --- Timestamp: microsecond precision ---


def test_timestamp_microsecond_precision():
    ts = dt.datetime(2025, 6, 15, 12, 30, 0, 123456, tzinfo=dt.UTC)
    result = t.Timestamp(ts)
    assert result.value.microsecond == 123456


def test_timestamp_millisecond_precision():
    ts = dt.datetime(2025, 6, 15, 12, 30, 0, 500000, tzinfo=dt.UTC)
    result = t.Timestamp(ts)
    assert result.value.microsecond == 500000


def test_timestamp_different_tz_offsets_same_instant():
    """Two different timezone offsets representing the same instant should produce equal results."""
    tz_plus5 = dt.timezone(dt.timedelta(hours=5))
    tz_minus5 = dt.timezone(dt.timedelta(hours=-5))
    ts1 = dt.datetime(2025, 6, 15, 17, 30, 0, tzinfo=tz_plus5)
    ts2 = dt.datetime(2025, 6, 15, 7, 30, 0, tzinfo=tz_minus5)
    r1 = t.Timestamp(ts1)
    r2 = t.Timestamp(ts2)
    assert r1.to_millis() == r2.to_millis()
    assert r1.value == r2.value
