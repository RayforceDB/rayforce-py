# :material-table-eye: Access Table Values

Rayforce-Py provides a handy interface to access [:octicons-table-24: Table](overview.md) columns and values.

## Row Count

Use the built-in `len()` function to get the number of rows in a table:

```python
>>> table = Table({
    "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
    "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
    "age": Vector(items=[29, 34, 41], ray_type=I64),
})

>>> len(table)
3
```

## Bracket Notation Access

You can use Python's bracket notation to access columns directly:

**Single column** - returns a [:material-vector-line: Vector](../vector.md):

```python
>>> table["name"]
Vector([Symbol('alice'), Symbol('bob'), Symbol('charlie')])

>>> table["age"]
Vector([I64(29), I64(34), I64(41)])
```

**Multiple columns** - returns a new [:octicons-table-24: Table](overview.md):

```python
>>> table[["id", "name"]]
Table(columns=['id', 'name'])
```

## Access a Specific Column

The `at_column()` method returns all values from a specific column as a [:material-vector-line: Vector](../vector.md).

```python
>>> table = Table({
    "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
    "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
    "age": Vector(items=[29, 34, 41], ray_type=I64),
})

>>> name_col = table.at_column("name")
>>> name_col
Vector([Symbol('alice'), Symbol('bob'), Symbol('charlie')])

>>> age_col = table.at_column("age")
>>> age_col
Vector([I64(29), I64(34), I64(41)])
```

## Access a Specific Row

The `at_row()` method returns all column values for a specific row as a [:material-code-braces: Dict](../dict.md). The row index is zero-based.

```python
>>> table = Table({
    "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
    "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
    "age": Vector(items=[29, 34, 41], ray_type=I64),
})

>>> row_0 = table.at_row(0)
>>> row_0
Dict({'id': '001', 'name': 'alice', 'age': 29})

>>> row_0.to_python()
{'id': '001', 'name': 'alice', 'age': 29}

>>> row_2 = table.at_row(2)
>>> row_2.to_python()
{'id': '003', 'name': 'charlie', 'age': 41}
```

## Take Rows from a Table

The `take()` method returns a new table containing a subset of rows from the original table.

When called with a single argument, it takes the first `n` rows:

```python
>>> table = Table({
    "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
    "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
    "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
})

>>> first_two = table.take(2)
>>> print(first_two)
┌────────┬────────┬────────────────────┐
│   id   │  name  │        age         │
│ SYMBOL │ SYMBOL │        I64         │
├────────┼────────┼────────────────────┤
│ 001    │ alice  │ 29                 │
│ 002    │ bob    │ 34                 │
├────────┴────────┴────────────────────┤
│ 2 rows (2 shown) 3 columns (3 shown) │
└──────────────────────────────────────┘
```

When called with an `offset` argument, it takes `n` rows starting from the offset:

```python
>>> middle_rows = table.take(2, offset=1)
>>> print(middle_rows)
┌────────┬─────────┬───────────────────┐
│   id   │  name   │        age        │
│ SYMBOL │ SYMBOL  │        I64        │
├────────┼─────────┼───────────────────┤
│ 002    │ bob     │ 34                │
│ 003    │ charlie │ 41                │
├────────┴─────────┴───────────────────┤
│ 2 rows (2 shown) 3 columns (3 shown) │
└──────────────────────────────────────┘
```

When called with a negative number, it takes the last `n` rows:

```python
>>> last_rows = table.take(-2)
>>> print(last_rows)
┌────────┬─────────┬───────────────────┐
│   id   │  name   │        age        │
│ SYMBOL │ SYMBOL  │        I64        │
├────────┼─────────┼───────────────────┤
│ 003    │ charlie │ 41                │
│ 004    │ dana    │ 38                │
├────────┴─────────┴───────────────────┤
│ 2 rows (2 shown) 3 columns (3 shown) │
└──────────────────────────────────────┘
```

## Head and Tail

The `head()` and `tail()` methods provide convenient shortcuts for getting the first or last rows:

```python
>>> table = Table({
    "id": Vector(items=["001", "002", "003", "004", "005"], ray_type=Symbol),
    "name": Vector(items=["alice", "bob", "charlie", "dana", "eve"], ray_type=Symbol),
    "age": Vector(items=[29, 34, 41, 38, 25], ray_type=I64),
})

>>> table.head(3)  # First 3 rows (default is 5)
Table(columns=['id', 'name', 'age'])

>>> table.tail(2)  # Last 2 rows (default is 5)
Table(columns=['id', 'name', 'age'])
```

## Column Types

The `dtypes` property returns a dictionary mapping column names to their data types:

```python
>>> table = Table({
    "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
    "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
    "age": Vector(items=[29, 34, 41], ray_type=I64),
    "salary": Vector(items=[50000.0, 60000.0, 70000.0], ray_type=F64),
})

>>> table.dtypes
{'id': 'SYMBOL', 'name': 'SYMBOL', 'age': 'I64', 'salary': 'F64'}
```

## Describe

The `describe()` method returns summary statistics for numeric columns:

```python
>>> table = Table({
    "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
    "age": Vector(items=[29, 34, 41], ray_type=I64),
    "salary": Vector(items=[50000.0, 60000.0, 70000.0], ray_type=F64),
})

>>> table.describe()
{
    'age': {'count': 3, 'mean': 34.666666666666664, 'min': 29, 'max': 41},
    'salary': {'count': 3, 'mean': 60000.0, 'min': 50000.0, 'max': 70000.0}
}
```

!!! note ""
    The `describe()` method only includes numeric columns (I64, F64, etc.) in its output.

## Get Column Names and Values

```python
>>> table: Table
>>> table.columns()
Vector([Symbol('symbol'), Symbol('time'), Symbol('bid'), Symbol('ask')])

>>> table.values()
List([
    Vector([Symbol('AAPL'), Symbol('AAPL'), Symbol('AAPL'), Symbol('GOOG'), Symbol('GOOG'), Symbol('GOOG')]),
    Vector([Time(datetime.time(9, 0, 0, 95000)), Time(datetime.time(9, 0, 0, 105000)), Time(datetime.time(9, 0, 0, 295000)), Time(datetime.time(9, 0, 0, 145000)), Time(datetime.time(9, 0, 0, 155000)), Time(datetime.time(9, 0, 0, 345000))]),
    Vector([F64(100.0), F64(101.0), F64(102.0), F64(200.0), F64(201.0), F64(202.0)]),
    Vector([F64(110.0), F64(111.0), F64(112.0), F64(210.0), F64(211.0), F64(212.0)])
])

>>> [column for column in [records[0] for records in table.values()]]
[Symbol('AAPL'), Time(datetime.time(9, 0, 0, 95000)), F64(100.0), F64(110.0)]
```
