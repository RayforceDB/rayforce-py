# :material-text: Symbol

The `Symbol` type represents an symbolic identifier, which is not mutable. Symbols are commonly used for table column names.

You can initialize a `Symbol` type from Python value, which supports `str()` conversion.

Accessing the value is possible via `.value` property.

### Usage
```python
>>> from rayforce import Symbol
>>> s = Symbol("RayforcePy")
>>> s
Symbol("RayforcePy")  # type: rayforce.Symbol
>>> s8.value
"RayforcePy"  # type: str
```
