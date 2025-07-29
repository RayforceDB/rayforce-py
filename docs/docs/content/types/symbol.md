# Symbol

The `Symbol` type represents an symbolic identified in raypy, which is not mutable. Symbols are commonly used for function and env var names.

- Any Python value can be converted to a Symbol (via string conversion)
- Symbols are immutable once created
- Comparison works only between Symbol instances

## Type Information

| Type | Rayforce Object Type Code |
|------|---------------------------|
| `Symbol` | `-6` |


### Creating Symbol Values

```python
from raypy import types as t

>>> t.Symbol("this is a symbol")
Symbol(this is a symbol)

>>> t.Symbol(123)
Symbol(123)
```

### Accessing Values

```python
>>> s = t.Symbol("symbol")
>>> s
Symbol("symbol")

>>> s.value
"symbol"
```

### Comparison

```python
>>> s1 = t.Symbol("test")
>>> s2 = t.Symbol("test")
>>> s3 = t.Symbol("other")

>>> s1 == s2
True

>>> s1 == s3
False
```

### Type Conversion

```python
>>> t.Symbol("hello")
Symbol("hello")

>>> t.Symbol(42)
Symbol(42)

>>> Symbol(3.14)
Symbol(3.14)

>>> Symbol(True)
Symbol(True)

```
