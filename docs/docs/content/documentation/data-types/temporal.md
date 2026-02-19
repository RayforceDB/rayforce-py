# :material-clock-time-two: Temporal Types

There are 3 temporal types in Rayforce-Py:

| Rayforce-Py Type | Low level representation                     | Python representation |
|------------------|----------------------------------------------|-----------------------|
| `Date`           | Number of days since January 1st 2000        | datetime.date         |
| `Time`           | Number of miliseconds since 00:00            | datetime.time         |
| `Timestamp`      | Number of nanoseconds since January 1st 2000 | datetime.timestamp    |


### Date Usage
```python
>>> import datetime as dt
>>> from rayforce import Date

>>> date = Date(dt.date(year=2025, month=5, day=10))  # As datetime.date object
>>> date
Date(datetime.date(2025, 5, 10))

>>> date = Date("2025-05-10")  # As isoformat string
>>> date
Date(datetime.date(2025, 5, 10))

>>> date = Date(9261)  # As number of days since 2000-01-01
>>> date
Date(datetime.date(2025, 5, 10))

>>> date.value
datetime.date(2025, 5, 10)
```

### Time Usage
```python
>>> import datetime as dt
>>> from rayforce import Time

>>> time = Time(dt.time(hour=14, minute=30, second=45))  # As datetime.time object
>>> time
Time(datetime.time(14, 30, 45))

>>> time = Time("14:30:45")  # As isoformat string
>>> time
Time(datetime.time(14, 30, 45))

>>> time = Time(52245000)  # As number of miliseconds since 00:00
>>> time
Time(datetime.time(14, 30, 45))

>>> time.value
datetime.time(14, 30, 45)
```


### Timestamp Usage
```python
>>> import datetime as dt
>>> from rayforce import Timestamp

>>> timestamp = Timestamp(
    dt.datetime(
        2025, 5, 10, 14, 30, 45,
        tzinfo=dt.timezone.utc,  # timezone is required
    )
)  # As datetime.datetime object
>>> timestamp
Timestamp(datetime.datetime(2025, 5, 10, 14, 30, 45, tzinfo=datetime.timezone.utc))

>>> timestamp = Timestamp("2025-05-10T14:30:45+00:00")  # As isoformat string
>>> timestamp
Timestamp(datetime.datetime(2025, 5, 10, 14, 30, 45, tzinfo=datetime.timezone.utc))

>>> timestamp = Timestamp(800202645000000000)  # As number of nanoseconds since 2000-01-01
>>> timestamp
Timestamp(datetime.datetime(2025, 5, 10, 14, 30, 45, tzinfo=datetime.timezone.utc))

>>> timestamp.value
>>> timestamp
datetime.datetime(2025, 5, 10, 14, 30, 45, tzinfo=datetime.timezone.utc)
```

### Shift Timezone

The `shift_tz()` method shifts a `Timestamp` by a timezone offset, returning a new `Timestamp`. The original value is not mutated. It accepts any `datetime.tzinfo`, including `datetime.timezone` and `zoneinfo.ZoneInfo`.

```python
>>> import datetime as dt
>>> from zoneinfo import ZoneInfo
>>> from rayforce import Timestamp

>>> ts = Timestamp(dt.datetime(2025, 6, 15, 12, 0, 0, tzinfo=dt.UTC))

>>> ts.shift_tz(dt.timezone(dt.timedelta(hours=5)))
Timestamp(datetime.datetime(2025, 6, 15, 17, 0, 0, tzinfo=datetime.timezone.utc))

>>> ts.shift_tz(dt.timezone(dt.timedelta(hours=-5)))
Timestamp(datetime.datetime(2025, 6, 15, 7, 0, 0, tzinfo=datetime.timezone.utc))

>>> ts.shift_tz(ZoneInfo("Etc/GMT-5"))  # Etc/GMT-5 = UTC+5
Timestamp(datetime.datetime(2025, 6, 15, 17, 0, 0, tzinfo=datetime.timezone.utc))
```

`shift_tz` is also available on `Column` for use in queries, allowing you to shift an entire column of timestamps:

```python
>>> import datetime as dt
>>> from rayforce import Table, Column

>>> result = table.select(
        "id",
        local_time=Column("created_at").shift_tz(dt.timezone(dt.timedelta(hours=3))),
    ).execute()
```
