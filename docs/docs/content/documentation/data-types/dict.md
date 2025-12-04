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
Vector[6]
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

# TODO: Add support for item assignment
```