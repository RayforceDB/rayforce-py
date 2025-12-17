# :material-help-circle: Frequently Asked Questions

## What is the difference between inplace and by reference operations?

Rayforce-Py supports two modes of operation for table queries: **inplace** and **by reference**. Understanding the difference is crucial for working effectively with tables.

### Inplace Operations

**Inplace operations** work directly on an in-memory `Table` object. The table exists as a Python object in your current session, typically created using methods like `Table.from_dict()`, `Table.from_csv()`, or returned from a previous query.

```python
>>> from rayforce import Table, Vector, Symbol, I64, Column

>>> # Create an in-memory table
>>> table = Table.from_dict({
...     "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
...     "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
...     "age": Vector(items=[29, 34, 41], ray_type=I64),
... })

>>> # Inplace operation - works directly on the table object
>>> result = table.update(age=100).where(Column("id") == "001").execute()
>>> result.values()[2][0].value  # age updated to 100
100
```

### By Reference Operations

**By reference operations** work on tables that have been saved to the Rayforce environment behind a Symbol using `table.save()`. These tables are stored in the Rayforce database and accessed via `Table.from_name()`.

```python
>>> # Create and save a table to the Rayforce environment
>>> table = Table.from_dict({
...     "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
...     "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
...     "age": Vector(items=[29, 34, 41], ray_type=I64),
... })
>>> table.save("my_table")  # Save to Rayforce environment

>>> # By reference operation - works on the saved table reference
>>> result = (
...     Table.from_name("my_table")
...     .update(age=100)
...     .where(Column("id") == "001")
...     .execute()
... )
>>> result.values()[2][0].value  # age updated to 100
100
```
