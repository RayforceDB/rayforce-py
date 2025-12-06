# :material-group: Group By and Aggregations

Group rows by one or more columns and compute aggregations using `.by()`

### Group by a single column
```python
>>> result = table.by("symbol").execute()
```

### Group by multiple columns
```python
>>> result = table.by("symbol", "level").execute()
```

### Aggregate query with group by
```python
>>> result = (
        table
        .select(
            "bid",
            bid_max=Column("bid").max()
        )
        .by("symbol", "level")
        .execute()
    )
```
