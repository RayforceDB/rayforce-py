# :material-select-search: Select Queries

Rayforce-Py allows you to build select queries to the tables.  You can select specific columns or compute new ones, the power is limitless!

!!! note ""
    The main approach to build the queries is to utilise chainable API, which reads left-to-right and builds the lazy query - until it's executed.

## :simple-dwavesystems: Selecting Uncomputed Columns

Just provide a strings as a non-keyword arguments to the `select()` method to fetch them.
```python
>>> result = table.select("id", "name", "age").execute()
```

If you wish to select all table columns which are available - pass `"*"`, just like with SQL.
```python
>>> result = table.select("*").execute()
```

## :material-calculator-variant-outline: Selecting Computed Columns

You can select new computed columns using expressions:
```python
>>> result = table.select(
        "id",
        total=Column("price") * Column("quantity"),
    ).execute()
```

!!! note ""
    The computed columns are named using keyword arguments, where the key is the column name and the value is the expression.
    Expression can be of any type, which can be assigned to the column. You can do math operations with the column, or perform
    more complex aggregations, which you can read about below.

    You need to use `Column` class to utilise it in computations or aggregations


## :material-checkbox-multiple-blank-outline: Using Aggregations

Rayforce-Py provides a number of aggregations you may use when querying computed columns

| Operation | Description |
|-----------|-------------|
| `sum()`   | Calculates the sum of the selected column |
| `mean()`/ `avg()`   | Calculates the average value of the selected column |
| `median()`   | Calculates the median value of the selected column |
| `min()`   | Calculates the min value of the selected column |
| `max()`   | Calculates the max value of the selected column |
| `count()`   | Calculates the count of the entries for selected column |
| `first()` | Retrieves the first value for selected column |
| `last()` | Retrieves the last value for selected column |
| `distinct()` | Gets the distinct value of the column |


### For Example:
```python
>>> scores = Table({
        "student_id": Vector([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], ray_type=I64),
        "score": Vector([85, 92, 78, 96, 88, 91, 83, 95, 87, 90], ray_type=I64),
        "subject": Vector(
            ["Math", "Math", "Science", "Science", "Math",
            "Science", "Math", "Science", "Math", "Chemistry"],
            ray_type=Symbol,
        ),
    })

>>> stats = scores.select(
        total_students=Column("student_id").count(),      # Count: number of records
        sum_scores=Column("score").sum(),                 # Sum: total of all scores
        avg_score=Column("score").mean(),                 # Mean: average score
        median_score=Column("score").median(),            # Median: middle value
        min_score=Column("score").min(),                  # Min: lowest score
        max_score=Column("score").max(),                  # Max: highest score
        first_student=Column("student_id").first(),       # First: first student ID
        last_subject=Column("subject").last()             # Last: last subject
    ).execute()
┌────────────────┬────────────┬───────────┬──────────────┬───────────┬───────────┬───────────────┬──────────────┐
│ total_students │ sum_scores │ avg_score │ median_score │ min_score │ max_score │ first_student │ last_subject │
├────────────────┼────────────┼───────────┼──────────────┼───────────┼───────────┼───────────────┼──────────────┤
│ 10             │ 885        │ 88.50     │ 89.00        │ 78        │ 96        │ 1             │ Chemistry    │
├────────────────┴────────────┴───────────┴──────────────┴───────────┴───────────┴───────────────┴──────────────┤
│ 1 rows (1 shown) 8 columns (8 shown)                                                                          │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

>>> unique_subjects = scores.select(
        subject=Column("subject").distinct()              # Distinct: unique values
    ).execute()
┌──────────────────────────────────────┐
│ subject                              │
├──────────────────────────────────────┤
│ Math                                 │
│ Science                              │
│ Chemistry                            │
├──────────────────────────────────────┤
│ 3 rows (3 shown) 1 columns (1 shown) │
└──────────────────────────────────────┘
```


## :material-filter: Using Filters

Filters are quite powerful in Rayforce-Py. You can implement them using `.where()` statement addressing the previous `.select()`

```python
>>> result = table.select("id", "name", "age").where(Column("age") >= 35).execute()
```

Library supports all standard comparison operators:

- `==` - Equal to
- `!=` - Not equal to
- `>` - Greater than
- `>=` - Greater than or equal to
- `<` - Less than
- `<=` - Less than or equal to

## IN Operator

Check if a value is in a list:

```python
>>> result = table.where(Column("dept").isin(["eng", "marketing"])).execute()
```

!!! note ""
    Just as with computed columns, `where` statements have to be an expression, addressing a specific computed or uncomputed column.

More complex example
```python
>>> result = table.select("id", "name", "age").where(
        (Column("age") >= 20) & Column("department").isin("IT", "HR", "Marketing")
    ).execute()
```

## Filtered Aggregations

You can apply filters to aggregations using the `where()` method on columns:

```python
>>> result = (
        table
        .select(
            total=Column("amount").sum(),
            active_total=Column("amount").where(Column("status") == "active").sum(),
            count=Column("amount").count(),
        )
        .by("category")
        .execute()
    )
```
!!! note ""
    This computes the total for all rows, but only sums active rows for `active_total`.
