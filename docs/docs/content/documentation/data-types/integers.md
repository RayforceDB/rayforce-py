# :octicons-number-24: Integer Types

There are three integer types available:

- `I16`. Range: `[32768, 32767]`
- `I32`. Range: `[-2147483648, 2147483647]`
- `I64`. Range: `[-9223372036854775808, 9223372036854775807]`

### Usage

You can initialize any integer type from Python value, which supports `int()` conversion.

Accessing the value is possible via `.value` property.
```python
>>> from rayforce import I16, I32, I64
>>> i16 = I16(123)
>>> i16
I16(123)  # type: rayforce.I16
>>> i16.value
123  # type: int

>>> i32 = I32(123)
>>> i32
I32(123)  # type: rayforce.I32
>>> i32.value
123  # type: int

>>> i64 = I64(123)
>>> i64
I64(123)  # type: rayforce.I64
>>> i64.value
123  # type: int
```
