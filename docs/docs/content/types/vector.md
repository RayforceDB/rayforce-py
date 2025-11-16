# Vector

The `Vector` type represents a collection of elements of a specific type and of a specific length. All elements in a vector must be of the same type. Otherwise - it becomes a `List` (type 0).


## Usage

### Creating Vector

```python
from raypy import Vector, I64, Symbol

# Empty vector with specific type
int_vector = Vector(type_code=I64.type_code, length=5)

# Vector with initial items
symbol_vector = Vector(
    type_code=Symbol.type_code,
    items=["apple", "banana", "cherry"]
)
```

### Accessing and Modifying Elements

```python
# Access elements by index
vector = Vector(type_code=I64.type_code, length=3)
vector[0] = 100
vector[1] = 200
vector[2] = 300

print(vector[0])  # 100
print(vector[1])  # 200
print(vector[2])  # 300

# Get all values as tuple
print(vector.value)  # (I64(100), I64(200), I64(300))
```

### Integer Vectors

```python
from raypy import Vector, I64

# Create integer vector
numbers = Vector(type_code=I64.type_code, length=5)

# Fill with values
for i in range(5):
    numbers[i] = (i + 1) * 10

print(f"Length: {len(numbers)}")  # 5
print(f"Values: {[num.value for num in numbers]}")  # [10, 20, 30, 40, 50]

# Iterate through vector
for i, value in enumerate(numbers):
    print(f"Index {i}: {value.value}")
```

## Notes

- All elements in a vector must be of the same scalar type
- Vector type is determined by the `type_code` parameter
- Length can be specified during creation or determined by initial items
- Supports positive and negative indexing
- Index out of bounds raises `IndexError`
- Vectors are iterable and support `len()`
- Use `.value` property to get all elements as a tuple
- Comparison works between vectors of the same type and length
