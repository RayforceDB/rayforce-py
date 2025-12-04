# :material-vector-line: Vector

The `Vector` type represents a collection of elements of a specific type. All elements in a vector must be of the same type. Otherwise - it becomes a [`List`](./list.md).


## Usage

```python
>>> from rayforce import Vector, I64, Symbol

>>> int_vector = Vector(type_code=I64.type_code, length=3)
>>> int_vector
Vector(5)  # 5 represents a type code of I64

>>> symbol_vector = Vector(type_code=Symbol.type_code, items=["apple", "banana", "cherry"])
>>> symbol_vector
Vector(5)  # 6 represents a type code of Symbol

>>> timestamp_vector = Vector(
    type_code=Timestamp.type_code,
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
