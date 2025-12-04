# :material-database-eye-outline: Query Guide

Rayforce-Py provides a powerful, chainable query API that makes it easy to work with data in RayforceDB. This guide covers all aspects of querying tables, from basic selections to complex aggregations and data modifications.

!!! note ""
    Rayforce-Py query API is designed to be intuitive and Pythonic. All queries are built using a fluent, chainable interface that reads naturally from left to right.

## :octicons-gear-24: Query Execution

All query operations are lazy by default. You must call `.execute()` to run the query and get results:

```python
# This builds the query but doesn't execute it
>>> query = table.select("id", "name").where(table.age >= 35)
# This actually runs the query and returns a Table
>>> result = query.execute()
```

## :fontawesome-solid-file-signature: Best Practices

**Chain Methods**: Take advantage of the fluent API to build readable queries:
```python
>>> result = (
        table.select("id", "name", "salary")
        .where(table.age >= 30)
        .where(table.dept == "eng")
        .execute()
    )
```

**Complex Conditions**: Use boolean-friendly operators for complex conditions:
```python
>>> result = table.select("id", "name", "salary").where(
        (table.age >= 30)
        & (table.salary > 100000)
    ).execute()
```

**Computed Columns**: Use computed columns to derive new data without modifying the original table:
```python
>>> result = table.select(
        "id",
        "price",
        "quantity",
        total=table.price * table.quantity,
    ).execute()
```

**Filtered Aggregations**: Use filtered aggregations in `by()` to compute conditional statistics:
```python
>>> result = (
        table
        .select(
            total=table.salary.sum(),
            high_earners=table.salary.where(table.salary > 100000).sum(),
        )
        .by("dept")
        .execute()
    )
```
