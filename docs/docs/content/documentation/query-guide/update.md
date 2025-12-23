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

!!! info "Inplace vs By Reference Operations"
    The `update()` operation can work with both in-memory tables (inplace) and saved tables (by reference).
    Learn more about the difference between [:material-help-circle: Inplace and by reference operations](../FAQ.md).
