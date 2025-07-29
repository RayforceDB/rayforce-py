# Data Types

raypy provides a comprehensive type system with both scalar and container types, designed for efficient data processing and type safety.

## Type System Overview

raypy's type system is built around two main categories:

- **Scalar Types**: Single values with specific data types
- **Container Types**: Collections and complex data structures

All types in raypy have unique type codes and provide efficient storage and operations optimized for data processing workflows.

## Scalar Types

Scalar types represent single values and are the building blocks of more complex data structures.

### Numeric Types

| Type | Description | Type Code | Range |
|------|-------------|-----------|-------|
| [I16](integers.md) | 16-bit signed integer | -3 | -32,768 to 32,767 |
| [I32](integers.md) | 32-bit signed integer | -4 | -2,147,483,648 to 2,147,483,647 |
| [I64](integers.md) | 64-bit signed integer | -5 | -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 |
| [F64](f64.md) | 64-bit floating point | -10 | ±1.7 × 10^308 with 15-17 digits precision |
| [U8](u8.md) | 8-bit unsigned integer | -2 | 0 to 255 |

### Text and Character Types

| Type | Description | Type Code | Usage |
|------|-------------|-----------|-------|
| [C8](c8.md) | Single character | -12 | Individual characters, tokens |
| [Symbol](symbol.md) | Symbolic identifier | -6 | Names, categories, constants |

### Boolean Type

| Type | Description | Type Code | Values |
|------|-------------|-----------|--------|
| [B8](b8.md) | Boolean value | -1 | True/False |

### Date and Time Types

| Type | Description | Type Code | Format |
|------|-------------|-----------|--------|
| [Date](date.md) | Calendar date | -7 | YYYY-MM-DD |
| [Time](time.md) | Time of day | -8 | HH:MM:SS.mmm |
| [Timestamp](timestamp.md) | Date and time | -9 | ISO 8601 format |

## Container Types

Container types hold collections of data and provide structured storage for complex information.

### Collection Types

| Type | Description | Type Code | Characteristics |
|------|-------------|-----------|-----------------|
| [Vector](vector.md) | Homogeneous collection | Variable | Same-type elements, typed |
| [List](list.md) | Heterogeneous collection | Dynamic | Mixed-type elements, flexible |
| [String](string.md) | Character sequence | 12 | Text data, UTF-8 support |

### Mapping and Structured Types

| Type | Description | Type Code | Use Cases |
|------|-------------|-----------|-----------|
| [Dict](dict.md) | Key-value mapping | Dynamic | Configuration, structured data |
| [Table](table.md) | Columnar data | Dynamic | Datasets, analytics, reporting |

### Identifier Types

| Type | Description | Type Code | Purpose |
|------|-------------|-----------|---------|
| [GUID](guid.md) | Globally unique identifier | 11 | Unique IDs, distributed systems |

## Type Conversion and Compatibility

### Automatic Conversion

raypy automatically converts Python types to appropriate raypy types:

```python
from raypy.types.scalar import I32, F64, B8, Symbol
from raypy.types.container import List, Dict

# Automatic conversion from Python types
number = I32(42)        # int -> I32
decimal = F64(3.14)     # float -> F64  
flag = B8(True)         # bool -> B8
name = Symbol("test")   # str -> Symbol

# Containers with mixed Python types
data = List([1, "hello", 3.14, True])  # Converts each element
config = Dict({"debug": True, "port": 8080})  # Converts values
```

### Type Safety

Each type enforces its constraints:

```python
from raypy.types.scalar import U8, C8

# Range validation
byte_val = U8(255)  # Valid: 0-255
# U8(256)  # Error: out of range

# Character validation  
char = C8("A")      # Valid: single character
# C8("ABC")  # Error: multiple characters
```

## Memory Efficiency

raypy types are designed for memory efficiency:

- **Scalar types** use precise storage (I16 uses 2 bytes, I32 uses 4 bytes)
- **Vectors** store homogeneous data efficiently
- **Containers** optimize for their specific use cases

## Performance Considerations

### When to Use Each Type

**Use Vectors when:**
- All elements are the same type
- Performing numerical computations
- Memory efficiency is important

**Use Lists when:**
- Elements have different types
- Structure is dynamic and changing
- Flexibility is more important than performance

**Use Dicts when:**
- Key-based lookup is needed
- Working with configuration or metadata
- Representing structured objects

**Use Tables when:**
- Working with columnar data
- Performing analytics or reporting
- Data has consistent schema

## Examples

### Basic Type Usage

```python
from raypy.types.scalar import I64, F64, Symbol, Date
from raypy.types.container import Vector, List, Dict, Table

# Scalar types
user_id = I64(12345)
score = F64(95.5)
status = Symbol("active")
signup_date = Date("2025-01-15")

# Container types
scores = Vector(type_code=F64.type_code, items=[95.5, 87.2, 92.1])
mixed_data = List([user_id, status, score])
user_profile = Dict({"id": 12345, "name": "Alice", "active": True})

# Table for structured data
columns = ["id", "name", "score"]
values = [[1, 2, 3], ["Alice", "Bob", "Charlie"], [95, 87, 92]]
leaderboard = Table(columns=columns, values=values)
```

### Type System Integration

```python
# Types work together seamlessly
from raypy.types.container import List, Dict
from raypy.types.scalar import Symbol, I64, F64

# Nested structures
user_data = Dict({
    "profile": Dict({
        "name": "Alice",
        "age": 29,
        "preferences": List([
            Symbol("dark_mode"),
            Symbol("notifications"), 
            Symbol("analytics")
        ])
    }),
    "scores": Vector(type_code=F64.type_code, items=[95.5, 87.2, 92.1]),
    "metadata": List([
        "last_login", "2025-01-15T10:30:00",
        "session_count", I64(42)
    ])
})
```

## Best Practices

1. **Choose the right precision**: Use I16/I32 for small numbers, I64 for large IDs
2. **Use appropriate containers**: Vectors for homogeneous data, Lists for mixed data
3. **Leverage type safety**: Let raypy catch type errors early
4. **Consider memory usage**: Smaller types use less memory
5. **Use Symbols for categories**: More efficient than strings for repeated values

## Next Steps

Explore each data type in detail:

- Start with [Scalar Types](integers.md) for basic data
- Learn about [Container Types](vector.md) for collections  
- Understand [Advanced Types](table.md) for structured data

Each type page includes comprehensive examples and usage patterns to help you get the most out of raypy's type system. 