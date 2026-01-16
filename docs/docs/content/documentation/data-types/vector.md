# :material-vector-line: Vector

The `Vector` type represents a collection of elements of a specific type. All elements in a vector must be of the same type. Otherwise - it becomes a [`List`](./list.md).


## Usage

```python
>>> from rayforce import Vector, I64, Symbol

>>> int_vector = Vector(ray_type=I64, length=3)
>>> int_vector
Vector(5)  # 5 represents a type code of I64

>>> symbol_vector = Vector(ray_type=Symbol, items=["apple", "banana", "cherry"])
>>> symbol_vector
Vector(5)  # 6 represents a type code of Symbol

>>> timestamp_vector = Vector(
    ray_type=Timestamp,
    items=[
        "2025-05-10T14:30:45+00:00",
        "2025-05-10T14:30:45+00:00",
        "2025-05-10T14:30:45+00:00",
    ]
)
```

### Accessing the values
```python
>>> [i for i in int_vector]
[I64(0), I64(0), I64(0), I64(0), I64(0)]

>>> [i for i in symbol_vector]
[Symbol('apple'), Symbol('banana'), Symbol('cherry')]
```

### Setting the values
```python
>>> int_vector[0] = 999
[I64(999), I64(0), I64(0), I64(0), I64(0)]
>>> int_vector

>>> symbol_vector[0] = "pineapple"
>>> [i for i in symbol_vector]
[Symbol('pineapple'), Symbol('banana'), Symbol('cherry')]

# TODO: Add push object to vector outside of it's length
```

## Operations

Vectors support a wide range of operations through mixins.

### Arithmetic Operations

```python
>>> v1 = Vector(ray_type=I64, items=[1, 2, 3])
>>> v2 = Vector(ray_type=I64, items=[4, 5, 6])

>>> v1 + v2
Vector([I64(5), I64(7), I64(9)])

>>> v1 * 2
Vector([I64(2), I64(4), I64(6)])

>>> v1 - v2
Vector([I64(-3), I64(-3), I64(-3)])
```

### Comparison Operations

```python
>>> v1 = Vector(ray_type=I64, items=[1, 5, 10])
>>> v2 = Vector(ray_type=I64, items=[2, 5, 8])

>>> v1 < v2
Vector([B8(True), B8(False), B8(False)])

>>> v1 >= v2
Vector([B8(False), B8(True), B8(True)])

>>> v1.eq(v2)
Vector([B8(False), B8(True), B8(False)])
```

### Logical Operations

```python
>>> v1 = Vector(ray_type=B8, items=[True, False, True])
>>> v2 = Vector(ray_type=B8, items=[True, True, False])

>>> v1.and_(v2)
Vector([B8(True), B8(False), B8(False)])

>>> v1.or_(v2)
Vector([B8(True), B8(True), B8(True)])

>>> v1.not_()
Vector([B8(False), B8(True), B8(False)])
```

### Aggregation Operations

```python
>>> v = Vector(ray_type=I64, items=[1, 2, 3, 4, 5])

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
>>> v = Vector(ray_type=I64, items=[10, 20, 30, 40, 50])

>>> v.first()
I64(10)

>>> v.last()
I64(50)

>>> v.take(3)
Vector([I64(10), I64(20), I64(30)])

>>> v.at(2)
I64(30)
```

### Set Operations

```python
>>> v1 = Vector(ray_type=I64, items=[1, 2, 3, 4])
>>> v2 = Vector(ray_type=I64, items=[3, 4, 5, 6])

>>> v1.union(v2)
Vector([I64(1), I64(2), I64(3), I64(4), I64(5), I64(6)])

>>> v1.sect(v2)
Vector([I64(3), I64(4)])

>>> v1.except_(v2)
Vector([I64(1), I64(2)])
```

### Search Operations

```python
>>> v = Vector(ray_type=I64, items=[10, 20, 30, 40])

>>> v.find(30)
I64(2)

>>> v.within(Vector(ray_type=I64, items=[15, 35]))
Vector([B8(False), B8(True), B8(True), B8(False)])

>>> mask = Vector(ray_type=B8, items=[True, False, True, False])
>>> v.filter(mask)
Vector([I64(10), I64(30)])
```

### Sort Operations

```python
>>> v = Vector(ray_type=I64, items=[3, 1, 4, 1, 5])

>>> v.asc()
Vector([I64(1), I64(1), I64(3), I64(4), I64(5)])

>>> v.desc()
Vector([I64(5), I64(4), I64(3), I64(1), I64(1)])

>>> v.iasc()  # indices for ascending sort
Vector([I64(1), I64(3), I64(0), I64(2), I64(4)])

>>> v.rank()
Vector([I64(2), I64(0), I64(3), I64(1), I64(4)])

>>> v.reverse()
Vector([I64(5), I64(1), I64(4), I64(1), I64(3)])

>>> v.negate()
Vector([I64(-3), I64(-1), I64(-4), I64(-1), I64(-5)])
```

### Functional Operations

```python
>>> from rayforce import Operation

>>> v = Vector(ray_type=I64, items=[1, 2, 3])
>>> v.map(Operation.NEGATE)
Vector([I64(-1), I64(-2), I64(-3)])
```
