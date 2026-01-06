# :material-function-variant: Functions

The `Fn` type represents a function (lambda) in RayforceDB. Functions allow you to define custom logic using RayforceDB's expression syntax and apply it to data in queries.

## Creating Functions

Functions are created from a string expression that starts with `(fn`:

```python
>>> from rayforce import Fn

>>> square = Fn("(fn [x] (* x x))")
>>> add = Fn("(fn [x y] (+ x y))")
```

!!! note ""
    The function string must start with `(fn` and follow RayforceDB's <a href="https://core.rayforcedb.com/content/documentation/data-types/functions.html">lambda syntax</a>: `(fn [args...] body)`

## Direct Function Calls

Functions can be called directly with scalar values:

```python
>>> square = Fn("(fn [x] (* x x))")
>>> square(5)
25
>>> square(10)
100

>>> add = Fn("(fn [x y] (+ x y))")
>>> add(5, 3)
8
>>> add(10, 20)
30
```

## Applying Functions to Columns

Functions can be applied to table columns using the `.apply()` method in queries:

```python
>>> from rayforce import Column, Fn, I64, Symbol, Table, Vector

>>> table = Table({
    "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
    "value": Vector(items=[2, 3, 4], ray_type=I64),
})

>>> square = Fn("(fn [x] (* x x))")

>>> result = table.select(
    "id",
    squared_value=square.apply(Column("value")),
).execute()

>>> result.at_column("squared_value")
Vector([I64(4), I64(9), I64(16)])
```

## Functions with Multiple Arguments

Functions can accept multiple arguments by applying them to multiple columns:

```python
>>> table = Table({
    "x": Vector(items=[2, 3, 4], ray_type=I64),
    "y": Vector(items=[3, 4, 5], ray_type=I64),
})

>>> sum_squares = Fn("(fn [x y] (+ (* x x) (* y y)))")

>>> result = table.select(
    "x",
    "y",
    sum_of_squares=sum_squares.apply(Column("x"), Column("y")),
).execute()

>>> result.at_column("sum_of_squares")
Vector([I64(13), I64(25), I64(41)])  # 2²+3²=13, 3²+4²=25, 4²+5²=41
```

## Functions with Aggregations

Functions can be combined with aggregation operations:

```python
>>> table = Table({
    "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
    "value": Vector(items=[2, 3, 4, 5], ray_type=I64),
})

>>> square = Fn("(fn [x] (* x x))")

>>> result = table.select(
    sum_of_squares=square.apply(Column("value")).sum(),
    avg_of_squares=square.apply(Column("value")).mean(),
    max_of_squares=square.apply(Column("value")).max(),
).execute()

>>> result.values()
List([Vector([I64(54)]), Vector([F64(13.5)]), Vector([I64(25)])])
```
