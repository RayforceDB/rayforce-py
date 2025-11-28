# F64 (Float)

The `F64` type represents floating-point number in raypy.

- Conversion from integers preserves the numeric value as a float
- String conversion supports standard float string formats
- As of now, comparison only works between `F64` instances

| Type | Rayforce Object Type Code | Size |
|------|---------------------------|-------|
| `F64` | `-10` | 64 bit |

### Creating F64 Values

```python
>>> from rayforce import types as t

>>> t.F64(3.14159)
F64(3.14159)

>>> t.F64(-42.5)
F64(-42.5)

>>> t.F64(123)
F64(123.0)

>>> t.F64("3.14159")
F64(3.14159)
```

### Accessing Values

```python
>>> f = t.F64(42.5)
>>> f.value
42.5
```
