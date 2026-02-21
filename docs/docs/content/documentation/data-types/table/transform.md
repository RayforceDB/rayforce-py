# :material-table-edit: Transform Tables

Rayforce-Py provides methods to transform [:octicons-table-24: Tables](overview.md) by modifying their structure.

## Add Columns

Use `select("*", col=value)` to add new columns to a table while keeping all existing ones. The `"*"` selects all current columns, and keyword arguments append new ones:

```python
>>> from rayforce import Table, Vector, Column, I64, Symbol

>>> table = Table({
    "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
    "id": Vector(items=[1, 2, 3], ray_type=I64),
})

>>> age = Vector(items=[20, 42, 93], ray_type=I64)
>>> table.select("*", age=age).execute()
Table(columns=['name', 'id', 'age'])
```

You can also add computed columns using expressions:

```python
>>> table.select("*", id_doubled=Column("id") * 2).execute()
Table(columns=['name', 'id', 'id_doubled'])
```

If the keyword argument matches an existing column name, it replaces that column:

```python
>>> new_ids = Vector(items=[10, 20, 30], ray_type=I64)
>>> table.select("*", id=new_ids).execute()
Table(columns=['name', 'id'])
```

## Drop Columns

The `drop()` method removes one or more columns from a table:

```python
>>> table = Table({
    "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
    "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
    "age": Vector(items=[29, 34, 41], ray_type=I64),
    "salary": Vector(items=[50000.0, 60000.0, 70000.0], ray_type=F64),
})

>>> table.drop("salary")
Table(columns=['id', 'name', 'age'])

>>> table.drop("age", "salary")
Table(columns=['id', 'name'])
```

## Rename Columns

The `rename()` method renames columns using a mapping dictionary:

```python
>>> table = Table({
    "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
    "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
    "age": Vector(items=[29, 34, 41], ray_type=I64),
})

>>> table.rename({"name": "employee_name", "age": "employee_age"})
Table(columns=['id', 'employee_name', 'employee_age'])

>>> table.rename({"id": "employee_id"})
Table(columns=['employee_id', 'name', 'age'])
```

## Cast Column Types

The `cast()` method changes the data type of a column:

```python
>>> table = Table({
    "id": Vector(items=[1, 2, 3], ray_type=I64),
    "value": Vector(items=[100.5, 200.7, 300.9], ray_type=F64),
})

>>> table.dtypes
{'id': 'I64', 'value': 'F64'}

>>> result = table.cast("value", I64)
>>> result.dtypes
{'id': 'I64', 'value': 'I64'}
```

!!! warning ""
    When casting between types, be aware of potential data loss. For example, casting F64 to I64 will truncate decimal values.

### Supported Type Conversions

Common type conversions include:

| From | To | Notes |
|------|-----|-------|
| F64 | I64 | Truncates decimal portion |
| I64 | F64 | Preserves value |
| Symbol | String | Converts symbol to string |
| String | Symbol | Converts string to symbol |

```python
>>> from rayforce import I64, F64, Symbol, String

>>> table = Table({
    "price": Vector(items=[99.99, 149.50, 299.00], ray_type=F64),
})

>>> table.cast("price", I64)  # Truncates to 99, 149, 299
Table(columns=['price'])
```
