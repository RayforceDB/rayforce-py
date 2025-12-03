# :material-check: Boolean

The `B8` type represents a boolean value.

You can initialize a `B8` type from Python value, which supports `bool()` conversion.

Accessing the value is possible via `.value` property.

### Usage
```python
>>> from rayforce import B8
>>> b8 = B8(True)
>>> b8
B8(True)  # type: rayforce.B8
>>> b8.value
True  # type: bool
```
