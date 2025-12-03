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
