# GROUP BY and Aggregations

Group rows by one or more columns and compute aggregations using `by()`

## Basic Group By

Group by a single column and compute aggregations:

```python
result = (
    table
    .select(
        avg_age=table.age.mean(),
        total_salary=table.salary.sum(),
        count=table.age.count(),
    )
    .by("dept")
    .execute()
```

## Multiple Group Columns

Group by multiple columns:

```python
result = (
    table
    .select(
        total_salary=table.salary.sum(),
        avg_salary=table.salary.mean(),
    )
    .by("dept", "level")
    .execute()
)
```

## Available Aggregation Functions

Rayforce-Py provides the following aggregation functions:

- **`sum()`** - Sum of values
- **`mean()`** or **`avg()`** - Average of values
- **`max()`** - Maximum value
- **`min()`** - Minimum value
- **`count()`** - Count of non-null values
- **`first()`** - First value in group
- **`last()`** - Last value in group
- **`median()`** - Median value
- **`distinct()`** - Distinct values

## Filtered Aggregations

You can apply filters to aggregations using the `where()` method on columns:

```python
result = (
    table
    .select(
        total=table.amount.sum(),
        active_total=table.amount.where(table.status == "active").sum(),
        count=table.amount.count(),
    )
    .by("category")
    .execute()
)
```

This computes the total for all rows, but only sums active rows for `active_total`.
