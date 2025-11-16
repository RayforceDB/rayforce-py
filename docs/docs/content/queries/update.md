# UPDATE Operations

Update existing rows in a table using the `update()` method combined with `where()`.


## Update Multiple Rows

Update all rows matching a condition:

```python
result = (
    Table.get("my_table")
    .update(salary=150000)
    .where(Table.get("my_table").dept == "eng")
    .execute()
)
```

## Update Multiple Columns

Update multiple columns at once:

```python
result = (
    Table.get("my_table")
    .update(age=30, salary=120000)
    .where(Table.get("my_table").id == "001")
    .execute()
)
```
