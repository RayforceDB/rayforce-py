# :material-format-letter-case: Char

The `C8` type represents a single character. It can hold exactly one character.

You can initialize a `C8` type from Python value, which supports `str()` conversion.

Accessing the value is possible via `.value` property.

### Usage
```python
>>> from rayforce import C8
>>> c8 = C8("R")
>>> c8
C8("R")  # type: rayforce.C8
>>> c8.value
"R"  # type: str
```
