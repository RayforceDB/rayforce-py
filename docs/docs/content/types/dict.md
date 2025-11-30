# Dict (Dictionary)

The `Dict` type represents a key-value mapping. It's similar to Python dictionaries.

## Usage

### Creating Dict Values

```python
from rayforce import Dict

# From Python dictionary
user_data = Dict({
    "name": "Alice",
    "age": 29,
    "active": True,
    "score": 95.5
})

# From nested dictionary
config = Dict({
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp"
    },
    "cache": {
        "enabled": True,
        "ttl": 3600
    }
})
```

### Accessing Keys and Values

```python
user = Dict({"name": "Alice", "age": 29})

# Get keys and values
keys = user.keys()
values = user.values()

print(f"Keys: {[k.value for k in keys]}")
print(f"Values: {[v.value for v in values]}")
```

### Dictionary Comparison

```python
# Compare dictionaries
dict1 = Dict({"name": "Alice", "age": 29})
dict2 = Dict({"name": "Alice", "age": 29})
dict3 = Dict({"name": "Bob", "age": 30})

print("Dictionary Comparison:")
print(f"dict1 keys: {[k.value for k in dict1.keys()]}")
print(f"dict1 values: {[v.value for v in dict1.values()]}")

print(f"dict1 == dict2: {dict1 == dict2}")  # True (same keys and values)
print(f"dict1 == dict3: {dict1 == dict3}")  # False (different values)
```

## Notes

- Dictionaries store key-value pairs.
- Use `.keys()` to get a vector of all keys
- Use `.values()` to get a list of all values
- Supports nested dictionaries and complex data structures
- Key order is preserved (insertion order)
- Comparison works between dictionaries with same keys and values
