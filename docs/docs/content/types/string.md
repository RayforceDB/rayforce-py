# String

The `String` type represents a vector of `c8` in raypy.

## Usage

### Creating String Values

```python
from rayforce import String

# From string literals
name = String("Hello, World!")
greeting = String("Welcome to raypy")
```

### Accessing Values

```python
text = String("Hello")
print(text.value)  # "Hello"
print(type(text.value))  # <class 'str'>
```

## Notes

- `String` is implemented as a vector of `C8` characters
- Variable length with dynamic sizing
- More efficient than individual `C8` objects for multi-character strings
- Supports all standard string operations through the `.value` property
- Length can be obtained using `len(string_obj)`
