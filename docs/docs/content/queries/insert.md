# INSERT Operations

Add new rows to a table using the `insert()` method.

## Insert Single Row

```python
table.save("my_table")

result = (
    Table.get("my_table")
    .insert(id="003", name="charlie", age=41)
    .execute()
)
```
