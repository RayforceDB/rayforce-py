# :octicons-sort-desc-24: Order By Queries

You can sort table results using the `order_by()` method, which integrates with the query chain.

## Basic Sorting

### Ascending sort (default)
```python
>>> result = table.order_by("salary").execute()
```

### Descending sort
```python
>>> result = table.order_by("salary", desc=True).execute()
```

## Sort by Multiple Columns
```python
>>> result = table.order_by("department", "salary").execute()
```

## Chaining with Other Operations

The `order_by()` method can be chained with `select()`, `where()`, and `by()`:

```python
>>> result = (
    table
    .select("name", "salary")
    .where(Column("salary") > 50000)
    .order_by("salary", desc=True)
    .execute()
)
```

```python
>>> result = (
    table
    .where(Column("department") == "Engineering")
    .order_by("name")
    .execute()
)
```

## Using Column Objects

You can use `Column` objects instead of strings:

```python
>>> from rayforce import Column

>>> result = table.order_by(Column("salary"), desc=True).execute()
```
