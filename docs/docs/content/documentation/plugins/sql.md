# :material-database-search: SQL Query Support

Rayforce-Py provides SQL query support, allowing you to query [:octicons-table-24: Tables](../data-types/table/overview.md) using familiar SQL syntax.

## Installation

The SQL integration requires the `sqlglot` library. Install it with:

```bash
pip install rayforce-py[sql]
```

Or install sqlglot directly:

```bash
pip install sqlglot
```

## Basic Usage

Use the `Table.sql()` method to execute SQL queries. Reference the table as `self` in your queries:

```python
>>> from rayforce import Table, Vector, I64, F64, Symbol

>>> employees = Table({
...     "id": Vector([1, 2, 3, 4, 5], ray_type=I64),
...     "name": Vector(["Alice", "Bob", "Charlie", "Diana", "Eve"], ray_type=Symbol),
...     "dept": Vector(["eng", "sales", "eng", "sales", "eng"], ray_type=Symbol),
...     "salary": Vector([120000, 75000, 95000, 80000, 110000], ray_type=I64),
... })

>>> result = employees.sql("SELECT * FROM self WHERE salary > 90000")
>>> print(result)
┌─────┬─────────┬────────┬────────┐
│ id  │  name   │  dept  │ salary │
│ I64 │ SYMBOL  │ SYMBOL │  I64   │
├─────┼─────────┼────────┼────────┤
│ 1   │ Alice   │ eng    │ 120000 │
│ 3   │ Charlie │ eng    │ 95000  │
│ 5   │ Eve     │ eng    │ 110000 │
└─────┴─────────┴────────┴────────┘
```

## Supported SQL Features

### SELECT Columns

Select specific columns or all columns with `*`:

```python
# Select all columns
employees.sql("SELECT * FROM self")

# Select specific columns
employees.sql("SELECT name, salary FROM self")

# Select with aliases
employees.sql("SELECT name AS employee_name, salary AS annual_salary FROM self")
```

### WHERE Clause

Filter rows using comparison operators and logical conditions:

```python
# Basic comparisons: =, !=, >, >=, <, <=
employees.sql("SELECT * FROM self WHERE salary > 100000")
employees.sql("SELECT * FROM self WHERE dept = 'eng'")

# Logical operators: AND, OR, NOT
employees.sql("SELECT * FROM self WHERE dept = 'eng' AND salary > 100000")
employees.sql("SELECT * FROM self WHERE dept = 'eng' OR dept = 'sales'")

# Parentheses for grouping
employees.sql("SELECT * FROM self WHERE (dept = 'eng' OR dept = 'sales') AND salary > 90000")

# IN clause
employees.sql("SELECT * FROM self WHERE dept IN ('eng', 'hr', 'sales')")
employees.sql("SELECT * FROM self WHERE id IN (1, 3, 5)")
```

### Aggregations

Use aggregate functions with or without GROUP BY:

```python
# Without GROUP BY (aggregate entire table)
employees.sql("SELECT COUNT(id) AS total, AVG(salary) AS avg_salary FROM self")

# Supported aggregations: COUNT, SUM, AVG, MIN, MAX, FIRST, LAST, MEDIAN
employees.sql("SELECT MIN(salary) AS min_sal, MAX(salary) AS max_sal FROM self")
```

### GROUP BY

Group rows and apply aggregations:

```python
>>> result = employees.sql("""
...     SELECT
...         dept,
...         COUNT(id) AS headcount,
...         AVG(salary) AS avg_salary,
...         MAX(salary) AS max_salary
...     FROM self
...     GROUP BY dept
... """)
>>> print(result)
┌────────┬───────────┬────────────┬────────────┐
│  dept  │ headcount │ avg_salary │ max_salary │
│ SYMBOL │    I64    │    F64     │    I64     │
├────────┼───────────┼────────────┼────────────┤
│ eng    │ 3         │ 108333.33  │ 120000     │
│ sales  │ 2         │ 77500.00   │ 80000      │
└────────┴───────────┴────────────┴────────────┘
```

### ORDER BY

Sort results in ascending or descending order:

```python
# Ascending (default)
employees.sql("SELECT * FROM self ORDER BY salary")

# Descending
employees.sql("SELECT * FROM self ORDER BY salary DESC")

# Combined with other clauses
employees.sql("""
    SELECT dept, AVG(salary) AS avg_sal
    FROM self
    GROUP BY dept
    ORDER BY avg_sal DESC
""")
```

### Computed Columns

Use arithmetic expressions in SELECT:

```python
# Arithmetic: +, -, *, /, %
employees.sql("SELECT name, salary, salary * 0.1 AS bonus FROM self")
employees.sql("SELECT name, salary / 12 AS monthly_salary FROM self")
employees.sql("SELECT name, salary + 5000 AS adjusted_salary FROM self")
```

## Limitations

The current SQL implementation supports common query patterns but has some limitations:

- Only `SELECT` statements are supported (no `INSERT`, `UPDATE`, `DELETE`)
- `JOIN` operations are not yet supported via SQL (use the native `.inner_join()`, `.left_join()` methods)
- Subqueries are not supported
- `HAVING` clause is not supported
- `LIMIT` and `OFFSET` are not supported (use `.take()` on the result)

For complex operations not supported by SQL, use the native Rayforce query API which provides full functionality.
