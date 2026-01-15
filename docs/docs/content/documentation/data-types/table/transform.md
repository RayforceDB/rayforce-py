# :material-table-edit: Transform Tables

Rayforce-Py provides methods to transform [:octicons-table-24: Tables](overview.md) by modifying their structure.

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
