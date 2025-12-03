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
