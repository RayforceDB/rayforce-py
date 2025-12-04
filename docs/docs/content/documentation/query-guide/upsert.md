# :material-table-plus: Upsert Queries

Rayforce-Py allows you to execute upsert queries in multiple ways.

Upsert is different than insert [:material-table-plus: Insert](./insert.md). It uses `match_by_first` keyword argument

!!! warning ""
    **`match_by_first`** : `int`
        The number of first columns that Rayforce will search to find a match for updating. If no match is found, an insert is performed.

### Upserting a single record

Using args:
```python
>>> table.upsert(1, "Alice", 28.5, match_by_first=1).execute()
```
!!! note ""
    The order of arguments <b>must match</b> the order of the table columns.

Using kwargs:
```python
>>> table.upsert(
        id=1,
        name="Alice",
        age=28.5,
        match_by_first=1,
    ).execute()
```

### Upserting multiple records

Using args:
```python
>>> table.upsert(
        [1, 2, 3],
        ["Alice", "Bob", "Sam"],
        [28.5, 15.3, 10.2],
        match_by_first=1,
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
        match_by_first=1
    ).execute()
```

!!! warning ""
    It's important to know that `upsert()` operation doesn't modify the original table.
    To access the new table with upserted rows, assign the result of `.execute()` to a new variable.
