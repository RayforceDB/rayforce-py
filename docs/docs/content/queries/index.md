# Query Guide

RayPy provides a powerful, chainable query API that makes it easy to work with data in RayforceDB. This guide covers all aspects of querying tables, from basic selections to complex aggregations and data modifications.

## Overview

RayPy's query API is designed to be intuitive and Pythonic. All queries are built using a fluent, chainable interface that reads naturally from left to right.

## Query Types

- **[Creating Tables](tables.md)** - Different ways to create and load tables
- **[SELECT](select.md)** - Selecting columns and computing new ones
- **[WHERE](where.md)** - Filtering rows with conditions
- **[ORDER BY](order-by.md)** - Sorting query results
- **[GROUP BY](group-by.md)** - Grouping and aggregating data
- **[JOIN](join.md)** - Combining data from multiple tables
- **[UPDATE](update.md)** - Modifying existing rows
- **[INSERT](insert.md)** - Adding new rows
- **[UPSERT](upsert.md)** - Update or insert rows
- **[Table Management](management.md)** - Saving, loading, and viewing tables

## Query Execution

All query operations are lazy by default. You must call `.execute()` to run the query and get results:

```python
# This builds the query but doesn't execute it
query = table.select("id", "name").where(table.age >= 35)

# This actually runs the query and returns a Table
result = query.execute()
```

## Best Practices

1. **Save Before Modifying**: Always call `save()` on a table before using `update()`, `insert()`, or `upsert()`.

2. **Chain Methods**: Take advantage of the fluent API to build readable queries:
   ```python
   result = (
       table.select("id", "name", "salary")
       .where(table.age >= 30)
       .where(table.dept == "eng")
       .order_by("salary", ascending=False)
       .execute()
   )
   ```

3. **Complex Conditions**: Use boolean operators for complex conditions:
   ```python
   result = table.where((table.age >= 30) & (table.salary > 100000)).execute()
   ```

4. **Computed Columns**: Use computed columns to derive new data without modifying the original table:
   ```python
   result = table.select(
       "id",
       "price",
       "quantity",
       total=table.price * table.quantity,
   ).execute()
   ```

5. **Filtered Aggregations**: Use filtered aggregations in `group_by()` to compute conditional statistics:
   ```python
   result = table.group_by("dept").agg(
       total=table.salary.sum(),
       high_earners=table.salary.where(table.salary > 100000).sum(),
   ).execute()
   ```

## Complete Example

Here's a complete example that demonstrates many query features:

```python
from raypy import Table

# Create a table
employees = Table(
    columns=["id", "name", "age", "dept", "salary"],
    values=[
        ["001", "002", "003", "004", "005"],
        ["alice", "bob", "charlie", "dana", "eli"],
        [29, 34, 41, 38, 45],
        ["eng", "eng", "marketing", "eng", "marketing"],
        [100000, 120000, 90000, 85000, 95000],
    ],
)

# Save the table
employees.save("employees")

# Query: Find senior engineers with high salaries
employees_table = Table.get("employees")
senior_engineers = (
    employees_table
    .select("id", "name", "salary")
    .where(employees_table.dept == "eng")
    .where(employees_table.age >= 35)
    .where(employees_table.salary > 100000)
    .by(salary=employees_table.salary.desc())
    .execute()
)

# Aggregate: Department statistics
dept_stats = (
    Table.get("employees")
    .select(
        avg_age=Table.get("employees").age.mean(),
        total_salary=Table.get("employees").salary.sum(),
        avg_salary=Table.get("employees").salary.mean(),
        count=Table.get("employees").id.count(),
    )
    .by("dept")
    .execute()
)

# Update: Give raises to engineers
employees_table = Table.get("employees")
employees_table.update(salary=150000).where(
    employees_table.dept == "eng"
).execute()

# Insert: Add a new employee
Table.get("employees").insert(
    id="006", name="frank", age=32, dept="hr", salary=75000
).execute()

# Upsert: Update or insert an employee
Table.get("employees").upsert(
    {"id": "001", "name": "alice_updated", "age": 30, "dept": "eng", "salary": 110000},
    match_on="id",
).execute()

# View results
Table.get("employees").show(n=10)
```

