# Date

The `Date` type represents a calendar date (year, month, day) in raypy.

- Dates are stored internally as days since the Unix epoch (2001-01-01)
- Does not contain time information

## Type Information

| Type | Rayforce Object Type Code | Stored as |
|------|---------------------------|-------|
| `Date` | `-7` | Days since (2001-01-01) |


### Creating Date Values

```python
>>> import datetime as dt
>>> from raypy import types as t

>>> t.Date(dt.date.today())
Date(2025-02-25)

>>> t.Date(dt.date(2025, 5, 10))
Date(2025-05-10)

>>> t.Date("2025-05-10")
Date(2025-05-10)

>>> t.Date(20218)  # Days since 2001-01-01
Date(2025-05-10)
```

### Accessing Values

```python
>>> d = t.Date("2025-01-15")
>>> d
Date(2025-01-15)

>>> d.value
datetime.date(2025, 1, 15)
```
