# Vector

The `Vector` type represents a collection of elements of a specific type and of a specific length. All elements in a vector must be of the same type. Otherwise - it becomes a `List` (type 0).


## Usage

### Creating Vector

```python
from raypy.types.container import Vector
from raypy.types.scalar import I64, Symbol

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
from raypy.types.container import Vector
from raypy.types.scalar import I64

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

### Symbol Vectors

```python
from raypy.types.container import Vector
from raypy.types.scalar import Symbol

# Vector of column names
columns = Vector(type_code=Symbol.type_code, length=4)
column_names = ["id", "name", "email", "age"]

for idx, name in enumerate(column_names):
    columns[idx] = name

print("Database columns:")
for i, col in enumerate(columns):
    print(f"Column {i}: {col.value}")
```

### Vector Operations

```python
from raypy.types.container import Vector
from raypy.types.scalar import I64

# Create vector
scores = Vector(type_code=I64.type_code, items=[95, 87, 92, 78, 88])

# Vector properties
print(f"Vector length: {len(scores)}")
print(f"Vector type code: {scores.type_code}")

# Access with negative indices
print(f"Last element: {scores[-1].value}")
print(f"Second to last: {scores[-2].value}")

# Convert to tuple
scores_tuple = scores.value
print(f"As tuple: {scores_tuple}")
```

### Vector Comparison

```python
from raypy.types.container import Vector
from raypy.types.scalar import I64

# Create identical vectors
vector1 = Vector(type_code=I64.type_code, items=[1, 2, 3])
vector2 = Vector(type_code=I64.type_code, items=[1, 2, 3])
vector3 = Vector(type_code=I64.type_code, items=[1, 2, 4])

print(f"Vector 1: {[v.value for v in vector1]}")
print(f"Vector 2: {[v.value for v in vector2]}")
print(f"Vector 3: {[v.value for v in vector3]}")

print(f"vector1 == vector2: {vector1 == vector2}")  # True
print(f"vector1 == vector3: {vector1 == vector3}")  # False
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
