# Integer Types

There are three integer types in raypy - `I16`, `I32`, `I64`

- All integer types support conversion from `int`, `float`, and `str`.
- Float values are truncated (not rounded) when converted.
- Cross-type equality comparison is supported between all integer types.
- Values outside the valid range will cause a ValueError during creation.


| Type | Rayforce Object Type Code | Range |
|------|---------------------------|-------|
| `I16` | `-3` | -32,768 to 32,767 |
| `I32` | `-4` | -2,147,483,648 to 2,147,483,647 |
| `I64` | `-5` | -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 |



### Creating Integer Values

```python
>>> from raypy import types as t

# From integer values
>>> t.I16(1000)
I16(1000)

>>> t.I32(1000000)
I32(1000000)

>>> t.I64(1000000000000)
I64(1000000000000)

# From float values (will be truncated)
>>> t.I32(42.7)
I32(42)

# From string values
>>> t.I64("12345")
I64(12345)
```

### Accessing Values

```python
>>> i32 = t.I32(42)
>>> i32
I32(32)

>>> int_val.value
42
```

### Comparison

```python
>>> a = I32(100)
>>> b = I32(100)
>>> c = I64(100)

>>> a == b
True

>>> a == c  # cross-type comparison
True
```
