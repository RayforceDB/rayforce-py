# Timestamp

The `Timestamp` type represents a specific point in time (date and time) in raypy. 

- Timestamp strings must be in ISO format: "YYYY-MM-DDTHH:MM:SS"
- Invalid timestamp formats will raise `ValueError`
- Stored internally as milliseconds since Unix epoch

## Type Information

| Type | Rayforce Object Type Code | Stored as | Precision |
|------|---------------------------|-------|--------|
| `Timestamp` | `-9` | Milliseconds since Unix epoch (1970-01-01 00:00:00 UTC) | Milliseconds |


### Creating Timestamp Values

```python
>>> import datetime as dt
>>> from rayforce import types as t

>>> t.Timestamp(dt.datetime.now())
Timestamp(2025-02-25 22:18:05.435000)

>>> t.Timestamp(dt.datetime(2025, 2, 25, 12, 0, tzinfo=dt.timezone(dt.timedelta(hours=5))))
Timestamp(2025-02-25 08:00:00)

>>> t.Timestamp("2025-01-15T14:30:20")
Timestamp(2025-01-15 14:30:20)

>>> t.Timestamp("2025-01-15T14:30:20+05:00")
Timestamp(2025-01-15 09:30:20)

>>> t.Timestamp(1759655720000)
Timestamp(2025-10-05 10:15:20)
```

### Accessing Values

```python
>>> ts = t.Timestamp("2025-01-15T14:30:20")
>>> ts
Timestamp(2025-01-15 14:30:20)

>>> ts.value
datetime.datetime(2025, 1, 15, 14, 30, 20)
```
