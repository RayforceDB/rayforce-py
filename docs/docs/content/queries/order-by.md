# ORDER BY

### Order by functionality is still in progress

Sort results using the `order_by()` method:

## Basic Sorting

```python
result = (
    table
    .select("id", "name", "age")
    .where(table.age >= 30)
    .by(age=table.age.asc())
    .execute()
)
```

## Descending Order

```python
result = (
    table
    .by(age=table.age.desc())
    .execute()
)
```

## Multiple Sort Columns

Sort by multiple columns:

```python
result = (
    table
    .select("dept", "name", "salary")
    .by(
        dept=table.dept.asc(),
        salary=table.salary.desc(),
    )
    .execute()
)
```
