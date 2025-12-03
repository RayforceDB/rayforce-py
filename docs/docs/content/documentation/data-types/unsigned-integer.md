# :material-numeric-8-box: Unsigned 8-bit Integer

The `U8` type represents an unsigned 8-bit integer. Range: `[0, 255]`

### Usage

You can initialize `U8` type from Python value, which supports `int()` conversion.

Accessing the value is possible via `.value` property.

```python
>>> from rayforce import U8
>>> u8 = U8(123)
>>> u8
U8(123)  # type: rayforce.U8
>>> u8.value
123  # type: int
```
