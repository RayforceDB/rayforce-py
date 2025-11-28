import datetime as dt
from rayforce import types as t


def test_date():
    d = dt.date(year=2025, month=5, day=10)
    assert t.Date(d).value == d
    assert t.Date(9261).value == d
    assert t.Date("2025-05-10").value == d
