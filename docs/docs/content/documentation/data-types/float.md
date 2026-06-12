# :material-decimal: Float

The `F64` type represents a 64-bit floating-point number.

### Usage
You can initialize an `F64` from any Python value that supports `float()` conversion.

Access the underlying value via the `.value` property.

```python
>>> from rayforce import F64
>>> f64 = F64(123)
>>> f64
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

## 32-bit Float

The `F32` type stores a 32-bit floating-point value. It shares the same construction and `.value` interface as `F64`; arithmetic promotes to `F64`.

```python
>>> from rayforce import F32
>>> f32 = F32(1.5)
>>> f32
F32(1.5)  # type: rayforce.F32
>>> f32.value
1.5  # type: float
>>> F32(1.5) + F32(2.5)
F64(4.0)  # type: rayforce.F64
```
