# :material-table-plus: Upsert Queries

Rayforce-Py allows you to execute upsert queries in multiple ways.

Upsert is different than insert [:material-table-plus: Insert](./insert.md). It uses `key_columns` keyword argument

!!! warning ""
    **`key_columns`** : `int`
        The number of first columns that Rayforce will search to find a match for updating. If no match is found, an insert is performed.

### Upserting a single record

Using args:
```python
>>> table.upsert(1, "Alice", 28.5, key_columns=1).execute()
```
!!! note ""
    The order of arguments <b>must match</b> the order of the table columns.

Using kwargs:
```python
>>> table.upsert(
        id=1,
        name="Alice",
        age=28.5,
        key_columns=1,
    ).execute()
```

### Upserting multiple records

Using args:
```python
>>> table.upsert(
        [1, 2, 3],
        ["Alice", "Bob", "Sam"],
        [28.5, 15.3, 10.2],
        key_columns=1,
    ).execute()
```
!!! note ""
    The order of arguments <b>must match</b> the order of the table columns.

Using kwargs:
```python
>>> table.upsert(
        id=[1, 2, 3],
        name=["Alice", "Bob", "Sam"],
        age=[28.5, 15.3, 10.2],
        key_columns=1
    ).execute()
```

!!! info "Inplace vs By Reference Operations"
    The `upsert()` operation can work with both in-memory tables (inplace) and saved tables (by reference).
    Learn more about the difference between [:material-help-circle: Inplace and by reference operations](../FAQ.md).
