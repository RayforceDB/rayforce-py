# Time

The `Time` type represents a time of day (hours, minutes, seconds, milliseconds) in raypy.

- Time strings must be in ISO format: "HH:MM:SS" or "HH:MM:SS.mmm"
- Valid range: 00:00:00.000 to 23:59:59.999
- Invalid time formats or out-of-range values will raise `ValueError`
- Stored internally as milliseconds since midnight

## Type Information

| Type | Rayforce Object Type Code | Stored as | Range | Precision |
|------|---------------------------|-------|------|--------|
| `Time` | `-8` | Milliseconds since midnight | 00:00:00.000 to 23:59:59.999 | Milliseconds |

### Creating Time Values

```python
>>> import datetime as dt
>>> from rayforce import types as t

>>> t.Time(dt.time(9, 30, 0))
Time(09:30:00)

>>> t.Time("10:15:20")
Time(10:15:20)

>>> t.Time(36920000)
Time(10:15:20)
```

### Accessing Values

```python
>>> ti = t.Time("14:30:20")
>>> ti
Time(14:30:20)

>>> ti.value
datetime.time(14, 30, 20)
```
