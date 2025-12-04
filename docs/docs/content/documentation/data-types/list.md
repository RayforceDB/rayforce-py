# :material-code-array: List

The `List` type represents a heterogeneous collection. Unlike [:material-vector-line: Vector](./vector.md), lists can contain elements of different types, making them similar to Python lists.

## Usage
```python
>>> from rayforce import List

>>> items = List([1, "hello", 3.14, True])
>>> items
List([I64(1), Symbol('hello'), F64(3.14), B8(True)])

>>> items[0]
I64(1)

>>> [i for i in items]
[I64(1), Symbol('hello'), F64(3.14), B8(True)]

# TODO: Add list item assignment by index

>>> items.append(123)
>>> items
List([I64(1), Symbol('hello'), F64(3.14), B8(True), I64(123)])
```
