# :material-decimal: Float

The `F64` type represents floating-point number.

### Usage
You can initialize a `F64` type from Python value, which supports `float()` conversion.

Accessing the value is possible via `.value` property.

```python
>>> from rayforce import F64
>>> f64 = F64(123)
F64(123.0)  # type: rayforce.F64
>>> f64.value
123.0  # type: float
```

## Operations

Float types support arithmetic, comparison, and math operations.

### Arithmetic Operations

```python
>>> a = F64(10.5)
>>> b = F64(3.0)

>>> a + b
F64(13.5)

>>> a - b
F64(7.5)

>>> a * b
F64(31.5)

>>> a / b
F64(3.5)
```

### Comparison Operations

```python
>>> a = F64(10.5)
>>> b = F64(20.3)

>>> a < b
B8(True)

>>> a > b
B8(False)

>>> a.eq(b)
B8(False)
```

### Math Operations

```python
>>> f = F64(3.7)

>>> f.ceil()
F64(4.0)

>>> f.floor()
F64(3.0)

>>> f.round()
F64(4.0)
```
