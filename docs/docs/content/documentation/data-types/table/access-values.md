# :material-table-eye: Access Table Values

<b>This is a work in progress section.</b>

Rayforce-Py provides a handy interface to access [:octicons-table-24: Table](overview.md) columns and values.

```python
>>> table: Table
>>> table.columns
['id', 'name', 'age']  # type: list[str]

>>> table.values()
List([Vector(5), Vector(6), Vector(5), Vector(5)])

>>> [column for column in [records[0] for records in employee_table.values()]]
[I64(1), Symbol('Alice'), I64(25)]

# TODO: Return Rayforce types from .columns method
```
