# ORDER BY

### Order by functionality is still in progress

Sort results using the `order_by()` method:

## Basic Sorting

```python
result = (
    table.select("id", "name", "age")
    .where(table.age >= 30)
    .order_by("age", ascending=True)
    .execute()
)
```

## Descending Order

```python
result = table.order_by("age", ascending=False).execute()
```

## Multiple Sort Columns

Sort by multiple columns:

```python
result = (
    table.select("dept", "name", "salary")
    .order_by("dept", "salary", ascending=True)
    .execute()
)
```

## Using Column Methods

You can also use `.asc()` and `.desc()` methods on columns:

```python
result = table.order_by(table.age.asc(), table.name.desc()).execute()
```

