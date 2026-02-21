# :material-vector-line: Vector

The `Vector` type represents a collection of elements of a specific type. All elements in a vector must be of the same type. Otherwise - it becomes a [`List`](./list.md).


## Usage

The type is automatically inferred from the first item. You can also specify `ray_type` explicitly to cast items to a specific type.

```python
>>> from rayforce import Vector, I64, F64, Symbol

# Type is inferred from items
>>> int_vector = Vector([1, 2, 3])
>>> int_vector
[I64(1), I64(2), I64(3)]

>>> float_vector = Vector([1.5, 2.5, 3.5])
>>> float_vector
[F64(1.5), F64(2.5), F64(3.5)]

>>> symbol_vector = Vector(["apple", "banana", "cherry"])
>>> symbol_vector
[Symbol('apple'), Symbol('banana'), Symbol('cherry')]

# Explicit ray_type for casting
>>> Vector([1, 2, 3], ray_type=F64)
[F64(1.0), F64(2.0), F64(3.0)]

# Pre-allocate empty vector with specific type and length
>>> Vector(ray_type=I64, length=3)
[I64(0), I64(0), I64(0)]
```

### Accessing and Setting Values
```python
>>> v = Vector([10, 20, 30])
>>> v[0]
I64(10)

>>> v[0] = 999
>>> v
[I64(999), I64(20), I64(30)]

>>> [i for i in v]
[I64(999), I64(20), I64(30)]
```

## Creating from NumPy

Use `Vector.from_numpy()` to create a vector from a NumPy array via bulk memory copy:

```python
>>> import numpy as np
>>> from rayforce import Vector

>>> arr = np.array([10, 20, 30], dtype=np.int64)
>>> Vector.from_numpy(arr)
[I64(10), I64(20), I64(30)]

>>> arr = np.array([1.5, 2.5, 3.5], dtype=np.float64)
>>> Vector.from_numpy(arr)
[F64(1.5), F64(2.5), F64(3.5)]
```

Supported NumPy dtypes: `int16`, `int32`, `int64`, `float64`, `uint8`, `bool`, string arrays, and temporal types. You can also pass `ray_type` explicitly:

```python
>>> Vector.from_numpy(np.array([1, 2, 3], dtype=np.int64), ray_type=F64)
[F64(1.0), F64(2.0), F64(3.0)]
```

### Temporal arrays

`datetime64` arrays are converted to `Timestamp` (nanosecond precision) or `Date` (day precision), with automatic epoch adjustment from NumPy's 1970-01-01 to Rayforce's 2000-01-01:

```python
>>> Vector.from_numpy(np.array(["2025-01-01", "2025-06-15"], dtype="datetime64[ns]"))
[Timestamp(2025-01-01T00:00:00.000), Timestamp(2025-06-15T00:00:00.000)]

>>> Vector.from_numpy(np.array(["2025-01-01", "2025-12-31"], dtype="datetime64[D]"))
[Date(2025-01-01), Date(2025-12-31)]
```

`timedelta64[ms]` arrays are converted to `Time` (milliseconds since midnight):

```python
>>> Vector.from_numpy(np.array([45_000_000, 64_800_000], dtype="timedelta64[ms]"))
[Time(12:30:00.000), Time(18:00:00.000)]
```

## Converting to Python and NumPy

Use `to_list()` and `to_numpy()` to efficiently export vector data for use with external libraries. Both methods use a bulk memory copy from the underlying C buffer — orders of magnitude faster than element-by-element iteration.

### `to_list()`

Returns a Python list of native values:

```python
>>> v = Vector([1.5, 2.5, 3.5], ray_type=F64)
>>> v.to_list()
[1.5, 2.5, 3.5]

>>> v = Vector([10, 20, 30], ray_type=I64)
>>> v.to_list()
[10, 20, 30]

>>> v = Vector(["alice", "bob"], ray_type=Symbol)
>>> v.to_list()
['alice', 'bob']
```

### `to_numpy()`

Returns a NumPy array with zero-copy for numeric types:

```python
>>> import numpy as np

>>> v = Vector([1.5, 2.5, 3.5], ray_type=F64)
>>> v.to_numpy()
array([1.5, 2.5, 3.5])  # dtype: float64

>>> v = Vector([10, 20, 30], ray_type=I64)
>>> v.to_numpy()
array([10, 20, 30])  # dtype: int64
```

## Operations

Vectors support a wide range of operations through mixins.

### Arithmetic Operations

```python
>>> v1 = Vector([1, 2, 3])
>>> v2 = Vector([4, 5, 6])

>>> v1 + v2
[I64(5), I64(7), I64(9)]

>>> v1 * 2
[I64(2), I64(4), I64(6)]

>>> v1 - v2
[I64(-3), I64(-3), I64(-3)]
```

### Comparison Operations

```python
>>> v1 = Vector([1, 5, 10])
>>> v2 = Vector([2, 5, 8])

>>> v1 < v2
[B8(True), B8(False), B8(False)]

>>> v1 >= v2
[B8(False), B8(True), B8(True)]

>>> v1.eq(v2)
[B8(False), B8(True), B8(False)]
```

### Logical Operations

```python
>>> v1 = Vector([True, False, True])
>>> v2 = Vector([True, True, False])

>>> v1.and_(v2)
[B8(True), B8(False), B8(False)]

>>> v1.or_(v2)
[B8(True), B8(True), B8(True)]

>>> v1.not_()
[B8(False), B8(True), B8(False)]
```

### Aggregation Operations

```python
>>> v = Vector([1, 2, 3, 4, 5])

>>> v.sum()
I64(15)

>>> v.min()
I64(1)

>>> v.max()
I64(5)

>>> v.average()
F64(3.0)
```

### Element Access

```python
>>> v = Vector([10, 20, 30, 40, 50])

>>> v.first()
I64(10)

>>> v.last()
I64(50)

>>> v.take(3)
[I64(10), I64(20), I64(30)]

>>> v.at(2)
I64(30)
```

### Set Operations

```python
>>> v1 = Vector([1, 2, 3, 4])
>>> v2 = Vector([3, 4, 5, 6])

>>> v1.union(v2)
[I64(1), I64(2), I64(3), I64(4), I64(5), I64(6)]

>>> v1.sect(v2)
[I64(3), I64(4)]

>>> v1.except_(v2)
[I64(1), I64(2)]
```

### Search Operations

```python
>>> v = Vector([10, 20, 30, 40])

>>> v.find(30)
I64(2)

>>> v.within(Vector([15, 35]))
[B8(False), B8(True), B8(True), B8(False)]

>>> mask = Vector([True, False, True, False])
>>> v.filter(mask)
[I64(10), I64(30)]
```

### Sort Operations

```python
>>> v = Vector([3, 1, 4, 1, 5])

>>> v.asc()
[I64(1), I64(1), I64(3), I64(4), I64(5)]

>>> v.desc()
[I64(5), I64(4), I64(3), I64(1), I64(1)]

>>> v.iasc()  # indices for ascending sort
[I64(1), I64(3), I64(0), I64(2), I64(4)]

>>> v.rank()
[I64(2), I64(0), I64(3), I64(1), I64(4)]

>>> v.reverse()
[I64(5), I64(1), I64(4), I64(1), I64(3)]

>>> v.negate()
[I64(-3), I64(-1), I64(-4), I64(-1), I64(-5)]
```

### Functional Operations

```python
>>> from rayforce import Operation

>>> v = Vector([1, 2, 3])
>>> v.map(Operation.NEGATE)
[I64(-1), I64(-2), I64(-3)]
```
