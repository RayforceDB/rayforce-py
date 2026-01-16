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
