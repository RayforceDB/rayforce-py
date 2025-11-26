import datetime as dt
from raypy import types as t


def test_timestamp():
    dt_obj = dt.datetime(2025, 5, 10, 14, 30, 45, tzinfo=dt.timezone.utc)
    # Note: Timestamp comparison might need to account for timezone/millisecond precision
    result = t.Timestamp(dt_obj)

    assert result.dt().year == 2025
    assert result.dt().month == 5
    assert result.dt().day == 10
    assert result.dt().hour == 14
    assert result.dt().minute == 30
    assert result.dt().second == 45
