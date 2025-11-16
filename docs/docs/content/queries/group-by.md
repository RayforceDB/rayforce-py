# GROUP BY and Aggregations

Group rows by one or more columns and compute aggregations using `group_by()` and `agg()`.

## Basic Group By

Group by a single column and compute aggregations:

```python
result = table.group_by("dept").agg(
    avg_age=table.age.mean(),
    total_salary=table.salary.sum(),
    count=table.age.count(),
)
```

## Multiple Group Columns

Group by multiple columns:

```python
result = table.group_by("dept", "level").agg(
    total_salary=table.salary.sum(),
    avg_salary=table.salary.mean(),
)
```

## Available Aggregation Functions

RayPy provides the following aggregation functions:

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
result = table.group_by("category").agg(
    total=table.amount.sum(),
    active_total=table.amount.where(table.status == "active").sum(),
    count=table.amount.count(),
)
```

This computes the total for all rows, but only sums active rows for `active_total`.

## Example: Department Statistics

```python
table = Table(
    columns=["dept", "age", "salary"],
    values=[
        ["eng", "eng", "marketing", "marketing", "hr"],
        [29, 34, 41, 38, 35],
        [100000, 120000, 90000, 85000, 80000],
    ],
)

result = table.group_by("dept").agg(
    avg_age=table.age.mean(),
    total_salary=table.salary.sum(),
    count=table.age.count(),
)
```
