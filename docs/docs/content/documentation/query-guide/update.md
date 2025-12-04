# :material-table-sync: Update Queries

Update existing rows in a table using the `update()` method.

### Update all rows

```python
result = table.update(salary=150000).execute()
```

### Update rows matching the condition

```python
result = table.update(salary=150000).where(table.dept == "IT").execute()
```

!!! warning ""
    It's important to know that `update()` operation doesn't modify the original table.
    To access the new table with upserted rows, assign the result of `.execute()` to a new variable.
