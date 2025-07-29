# Vector

The `Vector` type represents a homogeneous collection of elements of a specific scalar type in raypy. All elements in a vector must be of the same type.

## Type Information

- **Type Code:** Set during initialization based on element type
- **Element Types:** Any scalar type (I16, I32, I64, F64, B8, C8, Date, Symbol, Time, Timestamp, U8)
- **Python Equivalent:** Typed list/array
- **Characteristics:** Fixed element type, dynamic length

## Usage

### Creating Vector Values

```python
from raypy.types.container import Vector
from raypy.types.scalar import I64, Symbol, F64

# Empty vector with specific type
int_vector = Vector(type_code=I64.type_code, length=5)

# Vector with initial items
symbol_vector = Vector(
    type_code=Symbol.type_code,
    items=["apple", "banana", "cherry"]
)

# Vector from existing values
float_values = [1.1, 2.2, 3.3, 4.4]
float_vector = Vector(
    type_code=F64.type_code,
    items=float_values
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

## Examples

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
print("Vector elements:")
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

# Alternative creation with items
departments = Vector(
    type_code=Symbol.type_code,
    items=["engineering", "marketing", "sales", "hr"]
)

print(f"Departments: {[dept.value for dept in departments]}")
```

### Float Vectors

```python
from raypy.types.container import Vector
from raypy.types.scalar import F64

# Temperature readings
temperatures = Vector(
    type_code=F64.type_code,
    items=[23.5, 24.1, 22.8, 25.2, 23.9]
)

print(f"Temperature readings: {len(temperatures)} values")
for i, temp in enumerate(temperatures):
    print(f"Reading {i+1}: {temp.value}°C")

# Calculate average
total = sum(temp.value for temp in temperatures)
average = total / len(temperatures)
print(f"Average temperature: {average:.1f}°C")
```

### Boolean Vectors

```python
from raypy.types.container import Vector
from raypy.types.scalar import B8

# Feature flags
features = Vector(
    type_code=B8.type_code,
    items=[True, False, True, False, True]
)

feature_names = ["dark_mode", "notifications", "analytics", "beta_features", "auto_save"]

print("Feature Status:")
for i, (name, enabled) in enumerate(zip(feature_names, features)):
    status = "✓" if enabled.value else "✗"
    print(f"{status} {name}: {enabled.value}")
```

### Date Vectors

```python
from raypy.types.container import Vector
from raypy.types.scalar import Date

# Project milestones
milestones = Vector(
    type_code=Date.type_code,
    items=[
        "2025-02-01",  # Project start
        "2025-04-15",  # Design complete
        "2025-07-01",  # Development complete
        "2025-08-31",  # Project end
    ]
)

milestone_names = ["Start", "Design Done", "Dev Done", "End"]

print("Project Timeline:")
for name, date in zip(milestone_names, milestones):
    print(f"{name}: {date.value}")
```

### Vector Operations

```python
from raypy.types.container import Vector
from raypy.types.scalar import I64

# Create vector
scores = Vector(type_code=I64.type_code, length=5)
score_values = [95, 87, 92, 78, 88]

# Fill vector
for i, score in enumerate(score_values):
    scores[i] = score

# Vector properties
print(f"Vector length: {len(scores)}")
print(f"Vector type code: {scores.type_code}")

# Access with negative indices
print(f"Last element: {scores[-1].value}")
print(f"Second to last: {scores[-2].value}")

# Convert to tuple
scores_tuple = scores.value
print(f"As tuple: {scores_tuple}")
print(f"Tuple type: {type(scores_tuple)}")
```

### Working with Indices

```python
from raypy.types.container import Vector
from raypy.types.scalar import Symbol

# Countries vector
countries = Vector(
    type_code=Symbol.type_code,
    items=["USA", "Canada", "Mexico", "Brazil", "Argentina"]
)

# Positive indexing
print(f"First country: {countries[0].value}")
print(f"Third country: {countries[2].value}")

# Negative indexing
print(f"Last country: {countries[-1].value}")
print(f"Second to last: {countries[-2].value}")

# Index bounds checking
try:
    invalid = countries[10]  # Out of range
except IndexError as e:
    print(f"Index error: {e}")

try:
    invalid = countries[-10]  # Out of range
except IndexError as e:
    print(f"Negative index error: {e}")
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

### Time Series Data

```python
from raypy.types.container import Vector
from raypy.types.scalar import Timestamp

# Server response times
timestamps = Vector(
    type_code=Timestamp.type_code,
    items=[
        "2025-01-15T10:00:00",
        "2025-01-15T10:05:00",
        "2025-01-15T10:10:00",
        "2025-01-15T10:15:00",
    ]
)

response_times = Vector(
    type_code=F64.type_code,
    items=[0.235, 0.189, 0.301, 0.156]
)

print("Performance Log:")
for time, response in zip(timestamps, response_times):
    dt_str = time.value.strftime("%H:%M:%S")
    print(f"{dt_str}: {response.value:.3f}s")
```

### Data Processing Pipeline

```python
from raypy.types.container import Vector
from raypy.types.scalar import F64, I64

# Raw sensor data
raw_data = Vector(
    type_code=F64.type_code,
    items=[23.1, 24.5, 22.8, 25.9, 23.4, 24.2]
)

# Process data: convert to integers (rounded)
processed = Vector(type_code=I64.type_code, length=len(raw_data))
for i, value in enumerate(raw_data):
    processed[i] = round(value.value)

print("Data Processing:")
print(f"Raw: {[v.value for v in raw_data]}")
print(f"Processed: {[v.value for v in processed]}")

# Statistics
raw_values = [v.value for v in raw_data]
print(f"Min: {min(raw_values)}")
print(f"Max: {max(raw_values)}")
print(f"Average: {sum(raw_values) / len(raw_values):.2f}")
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
- More memory-efficient than Python lists for homogeneous data
- Ideal for numerical computations, time series, and typed collections 