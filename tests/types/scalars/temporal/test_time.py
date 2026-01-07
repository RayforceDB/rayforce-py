import datetime as dt

from rayforce import types as t


def test_time():
    time_obj = dt.time(hour=14, minute=30, second=45)
    assert t.Time(time_obj).value == time_obj
    assert t.Time("14:30:45").value == time_obj
