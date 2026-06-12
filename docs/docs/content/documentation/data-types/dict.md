# :material-code-braces: Dict

The `Dict` type represents a key-value mapping. It's similar to Python dictionaries.

## Usage

### Creating Dict Values

```python
>>> from rayforce import Dict

>>> user_data = Dict({
        "name": "Alice",
        "age": 29,
        "active": True,
        "score": 95.5,
        "cache": {
            "enabled": True,
            "ttl": 3600
        }
    })
>>> user_data
Dict({'name': 'Alice', 'age': 29, 'active': True, 'score': 95.5, 'cache': {'enabled': True, 'ttl': 3600}})

>>> user_data.keys()
Vector([Symbol('name'), Symbol('age'), Symbol('active'), Symbol('score'), Symbol('cache')])
>>> [i for i in user_data.keys()]
[
    Symbol('name'),
    Symbol('age'),
    Symbol('active'),
    Symbol('score'),
    Symbol('cache'),
]

>>> user_data.values()
List([Symbol('Alice'), I64(29), B8(True), F64(95.5), Dict({'enabled': True, 'ttl': 3600})])

>>> user_data["docs"] = {"is_this_docs": True}  # Item assignment
>>> user_data
Dict({
    'name': 'Alice',
    'age': 29,
    'active': True,
    'score': 95.5,
    'cache': {'enabled': True, 'ttl': 3600},
    'docs': {'is_this_docs': True}
})
```

## Operations

Dicts support various operations through mixins.

### Key/Value Access

```python
>>> d = Dict({"a": 1, "b": 2, "c": 3})

>>> d.key()
Vector([Symbol('a'), Symbol('b'), Symbol('c')])

>>> d.value()
List([I64(1), I64(2), I64(3)])
```
