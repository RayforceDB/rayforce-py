# String

The `String` type represents a vector of c8 in raypy.

## Usage

### Creating String Values

```python
from raypy.types.container import String

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

### Text Processing

```python
# Document content
document = String("raypy is a library")
print(f"Document: {document.value}")
print(f"Length: {len(document)} characters")

# Multi-line text
code_snippet = String("""
def hello_world():
    print("Hello, World!")
    return True
""")

print(f"Code snippet:")
print(code_snippet.value)
```

### String Comparison

```python
# Text comparison
text1 = String("Hello World")
text2 = String("Hello World")
text3 = String("Hello, World!")

print(f"Text 1: '{text1.value}'")
print(f"Text 2: '{text2.value}'")
print(f"Text 3: '{text3.value}'")

# Compare underlying string values
print(f"text1 == text2: {text1.value == text2.value}")  # True
print(f"text1 == text3: {text1.value == text3.value}")  # False
```

## Notes

- `String` is implemented as a vector of `C8` characters
- Variable length with dynamic sizing
- More efficient than individual `C8` objects for multi-character strings
- Supports all standard string operations through the `.value` property
- Length can be obtained using `len(string_obj)`
- For single characters, use the `C8` scalar type instead
