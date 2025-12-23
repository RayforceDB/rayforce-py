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

!!! info "Inplace vs By Reference Operations"
    The `insert()` operation can work with both in-memory tables (inplace) and saved tables (by reference).
    Learn more about the difference between [:material-help-circle: Inplace and by reference operations](../FAQ.md).
