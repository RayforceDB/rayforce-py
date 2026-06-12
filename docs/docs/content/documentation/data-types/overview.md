## :octicons-database-16: Data Types


Rayforce-Py provides a comprehensive type system for most of Rayforce C level types, designed for efficient data processing and type safety.

## Type System Overview

Rayforce-Py type system is built around two main categories:

- **Scalar Types**: Single values with specific data types
- **Container Types**: Collections and complex data structures

!!! note ""
    All types in Rayforce-Py have unique type codes and provide efficient storage and operations optimized for data processing workflows.


| Type | Description | Type Code |
|------|-------------|-----------|
| [I16](integers.md) | 16-bit signed integer | -3 |
| [I32](integers.md) | 32-bit signed integer | -4 |
| [I64](integers.md) | 64-bit signed integer | -5 |
| [F32](float.md) | 32-bit floating point | -6 |
| [F64](float.md) | 64-bit floating point | -7 |
| [U8](unsigned-integer.md) | 8-bit unsigned integer | -2 |
| [Symbol](symbol.md) | Symbolic identifier | -12 |
| [B8](boolean.md) | Boolean value | -1 |
| [Date](temporal.md) | Calendar date | -8 |
| [Time](temporal.md) | Time of day | -9 |
| [Timestamp](temporal.md) | Date and time | -10 |
| [GUID](guid.md) | Globally unique identifier | -11 |
| [String](string.md) | Character sequence | -13 |
| [Vector](vector.md) | Homogeneous collection | Variable |
| [List](list.md) | Heterogeneous collection | 0 |
| [Dict](dict.md) | Key-value mapping | 99 |
| [Table](table/overview.md) | Columnar data | 98 |
| [Fn](function.md) | User defined function | 100 |

## Type Conversion and Compatibility

### Automatic Conversion

Rayforce-Py automatically converts Python types to appropriate types:

```python
from rayforce import I32, F64, B8, Symbol, List, Dict

# Automatic conversion from Python types
number = I32(42)        # int -> I32
decimal = F64(3.14)     # float -> F64
flag = B8(True)         # bool -> B8
name = Symbol("test")   # str -> Symbol

# Containers with mixed Python types
data = List([1, "hello", 3.14, True])
config = Dict({"debug": True, "port": 8080})
```
