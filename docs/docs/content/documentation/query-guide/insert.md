# :material-table-plus: Insert Queries

Rayforce-Py allows you to execute Insert queries in a multiple ways

### Inserting a single record

Using args:
```python
>>> table.insert(1, "Alice", 28.5).execute()
```
!!! note ""
    The order of args <b>has to match</b> the order of the table columns

Using kwargs:
```python
>>> table.insert(
        id=1,
        name="Alice",
        age=28.5
    ).execute()
```

### Inserting multiple records

Using args:
```python
>>> table.insert([1, 2, 3], ["Alice", "Bob", "Sam"], [28.5, 15.3, 10.2]).execute()
```
!!! note ""
    The order of args <b>has to match</b> the order of the table columns

Using kwargs:
```python
>>> table.insert(
        id=[1, 2, 3],
        name=["Alice", "Bob", "Sam"],
        age=[28.5, 15.3, 10.2]
    ).execute()
```

!!! warning ""
    It's important to know - `insert()` operation doesn't modify the original table.
    To access new table with inserted row, assign the result of `.execute()` operation to the new variable.
