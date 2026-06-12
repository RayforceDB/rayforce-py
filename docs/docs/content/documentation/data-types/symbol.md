# :material-text: Symbol

The `Symbol` type represents an immutable symbolic identifier. Symbols are commonly used for table column names.

You can initialize a `Symbol` from any Python value that supports `str()` conversion.

Access the underlying value via the `.value` property.

### Usage
```python
>>> from rayforce import Symbol
>>> s = Symbol("RayforcePy")
>>> s
Symbol('RayforcePy')  # type: rayforce.Symbol
>>> s.value
'RayforcePy'  # type: str
```
