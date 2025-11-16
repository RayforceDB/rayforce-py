# UPSERT Operations

Upsert (update or insert) rows using the `upsert()` method. If a row matching the specified keys exists, it will be updated; otherwise, a new row will be inserted.

## Upsert Single Row

Upsert a single row with a single match key:

```python
table.save("my_table")

result = (
    Table.get("my_table")
    .upsert({"id": "001", "name": "alice_updated", "age": 30}, match_on="id")
    .execute()
)
```

## Upsert Multiple Rows

Upsert multiple rows at once:

```python
result = (
    Table.get("my_table")
    .upsert(
        [
            {"id": "001", "name": "alice_new", "age": 30},
            {"id": "003", "name": "charlie", "age": 41},
        ],
        match_on="id",
    )
    .execute()
)
```
