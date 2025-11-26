import datetime as dt
from raypy import types as t


def test_timestamp():
    dt_obj = dt.datetime(2025, 5, 10, 14, 30, 45, tzinfo=dt.timezone.utc)
    # Note: Timestamp comparison might need to account for timezone/millisecond precision
    result = t.Timestamp(dt_obj)

    assert result.value.year == 2025
    assert result.value.month == 5
    assert result.value.day == 10
    assert result.value.hour == 14
    assert result.value.minute == 30
    assert result.value.second == 45
