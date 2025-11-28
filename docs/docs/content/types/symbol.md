# Symbol

The `Symbol` type represents an symbolic identified in raypy, which is not mutable. Symbols are commonly used for table column names.

- Any Python value can be converted to a Symbol (via string conversion)
- Symbols are immutable once created
- Comparison works only between Symbol instances

## Type Information

| Type | Rayforce Object Type Code |
|------|---------------------------|
| `Symbol` | `-6` |


### Creating Symbol Values

```python
from rayforce import types as t

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
