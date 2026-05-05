import datetime as dt

import pytest

from rayforce import types as t


@pytest.mark.parametrize(
    "input_val,expected",
    [
        (dt.time(14, 30, 45), dt.time(14, 30, 45)),
        ("14:30:45", dt.time(14, 30, 45)),
    ],
)
def test_time(input_val, expected):
    assert t.Time(input_val).value == expected


# --- Time: millisecond precision via string parsing ---


@pytest.mark.parametrize(
    "input_str,expected_millis",
    [
        ("12:00:00.000", 43_200_000),
        ("12:00:00.500", 43_200_500),
        ("12:00:00.001", 43_200_001),
        ("14:30:45.123", 52_245_123),
    ],
)
def test_time_millisecond_precision_from_string(input_str, expected_millis):
    result = t.Time(input_str)
    assert result.to_millis() == expected_millis


@pytest.mark.parametrize(
    "input_str,expected_microseconds",
    [
        ("12:00:00.500", 500_000),  # 500ms = 500000us
        ("12:00:00.001", 1_000),  # 1ms = 1000us
    ],
)
def test_time_microsecond_in_value_from_string(input_str, expected_microseconds):
    """Time stores milliseconds; to_python() converts ms remainder to microseconds."""
    result = t.Time(input_str)
    assert result.value.microsecond == expected_microseconds


# --- Time: edge values ---


def test_time_midnight():
    result = t.Time(dt.time(0, 0, 0))
    assert result.value == dt.time(0, 0, 0)
    assert result.to_millis() == 0


def test_time_midnight_from_string():
    result = t.Time("00:00:00")
    assert result.value == dt.time(0, 0, 0)
    assert result.to_millis() == 0


def test_time_end_of_day():
    result = t.Time(dt.time(23, 59, 59))
    assert result.value == dt.time(23, 59, 59)
    assert result.to_millis() == 86_399_000


def test_time_end_of_day_with_millis_from_string():
    result = t.Time("23:59:59.999")
    assert result.to_millis() == 86_399_999
    assert result.value == dt.time(23, 59, 59, 999_000)
