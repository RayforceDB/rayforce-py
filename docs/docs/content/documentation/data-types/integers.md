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

## Operations

Integer types support arithmetic, comparison, and math operations.

### Arithmetic Operations

```python
>>> a = I64(10)
>>> b = I64(3)

>>> a + b
I64(13)

>>> a - b
I64(7)

>>> a * b
I64(30)

>>> a / b
I64(3)

>>> a % b
I64(1)
```

### Comparison Operations

```python
>>> a = I64(10)
>>> b = I64(20)

>>> a < b
B8(True)

>>> a > b
B8(False)

>>> a <= b
B8(True)

>>> a.eq(b)
B8(False)

>>> a.ne(b)
B8(True)
```

### Math Operations

```python
>>> from rayforce import F64

>>> f = F64(3.7)

>>> f.ceil()
F64(4.0)

>>> f.floor()
F64(3.0)

>>> f.round()
F64(4.0)
```
