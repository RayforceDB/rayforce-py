# List

The `List` type represents a heterogeneous collection. Unlike vectors, lists can contain elements of different types, making them similar to Python lists.

## Usage

### Creating List Values

```python
from raypy.types.container import List

# From Python list
mixed_list = List([1, "hello", 3.14, True])

# From raypy objects
from raypy.types.scalar import I64, Symbol, F64, B8
mixed_list = List([
    I64(42),
    Symbol("test"),
    F64(3.14),
    B8(True)
])

# Empty list
empty_list = List([])
```

### Accessing and Modifying Elements

```python
# Create and modify list
data = List([1, 2, 3])
print(f"Original: {[item.value for item in data]}")

# Modify elements
data[1] = "changed"
print(f"Modified: {[item.value for item in data]}")

# Access elements
print(f"First element: {data[0].value}")
print(f"Last element: {data[-1].value}")
```

### Nested Structures

```python
# Nested lists and complex data
nested_data = List([
    "users",
    List([
        List(["alice", 25, True]),
        List(["bob", 30, False]),
        List(["charlie", 28, True])
    ]),
    "settings",
    List([
        "theme", "dark",
        "language", "en",
        "notifications", True
    ])
])

print("Nested Data Structure:")
print(f"Length: {len(nested_data)}")

# Access nested elements
users_list = nested_data[1]
first_user = users_list[0]
print(f"First user: {[item.value for item in first_user]}")
```

## Notes

- Lists can contain elements of different types (heterogeneous)
- Supports nesting of lists, vectors, and other containers
- Length can be obtained using `len(list_obj)`
- Supports positive and negative indexing
- Index out of bounds raises `IndexError`
- Comparison works between lists with same structure and values
