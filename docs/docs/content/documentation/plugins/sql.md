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

## UPDATE Statements

Modify existing rows using UPDATE with SET and optional WHERE:

```python
# Update all rows
employees.sql("UPDATE self SET salary = 50000.0")

# Update with WHERE clause
employees.sql("UPDATE self SET salary = 100000.0 WHERE level = 'senior'")

# Update multiple columns
employees.sql("UPDATE self SET salary = 75000.0, level = 'mid' WHERE id = 5")

# Update with expressions (using column values)
employees.sql("UPDATE self SET salary = salary * 1.1 WHERE rating > 4.0")

# Update with complex WHERE
employees.sql("UPDATE self SET salary = salary + 5000.0 WHERE (dept = 'eng' OR dept = 'sales') AND years > 3")
```

**Note:** UPDATE returns the modified table. The original table is not mutated.

## INSERT Statements

Add new rows to a table using INSERT with VALUES:

```python
>>> employees = Table({
...     "id": Vector([1, 2], ray_type=I64),
...     "name": Vector(["Alice", "Bob"], ray_type=Symbol),
...     "salary": Vector([50000.0, 60000.0], ray_type=F64),
... })

# Insert single row with column names
>>> result = employees.sql("INSERT INTO self (id, name, salary) VALUES (3, 'Charlie', 70000.0)")
>>> print(len(result))
3

# Insert multiple rows
>>> result = employees.sql("""
...     INSERT INTO self (id, name, salary)
...     VALUES (4, 'Diana', 55000.0), (5, 'Eve', 65000.0)
... """)
>>> print(len(result))
5

# Insert without column names (values must match table column order)
>>> result = employees.sql("INSERT INTO self VALUES (6, 'Frank', 72000.0)")
```

**Note:** INSERT returns a new table with the added rows. The original table is not mutated.

## UPSERT (INSERT ... ON CONFLICT)

Perform upsert operations (insert or update) using the `ON CONFLICT` clause:

```python
>>> products = Table({
...     "id": Vector([1, 2], ray_type=I64),
...     "name": Vector(["Widget", "Gadget"], ray_type=Symbol),
...     "price": Vector([10.0, 20.0], ray_type=F64),
... })

# Update existing row (id=1 exists)
>>> result = products.sql("""
...     INSERT INTO self (id, name, price)
...     VALUES (1, 'Widget Pro', 15.0)
...     ON CONFLICT (id) DO UPDATE
... """)
>>> print(result["name"][0].value)
Widget Pro

# Insert new row (id=3 doesn't exist)
>>> result = products.sql("""
...     INSERT INTO self (id, name, price)
...     VALUES (3, 'Gizmo', 30.0)
...     ON CONFLICT (id) DO UPDATE
... """)
>>> print(len(result))
3

# Upsert multiple rows at once
>>> result = products.sql("""
...     INSERT INTO self (id, name, price)
...     VALUES (1, 'Widget Updated', 12.0), (4, 'Doohickey', 25.0)
...     ON CONFLICT (id) DO UPDATE
... """)
```

### Composite Keys

Use multiple columns as the conflict key by listing them in the `ON CONFLICT` clause:

```python
>>> inventory = Table({
...     "region": Vector(["US", "EU"], ray_type=Symbol),
...     "sku": Vector(["A001", "A001"], ray_type=Symbol),
...     "quantity": Vector([100, 50], ray_type=I64),
... })

# Use (region, sku) as composite key
>>> result = inventory.sql("""
...     INSERT INTO self (region, sku, quantity)
...     VALUES ('US', 'A001', 150)
...     ON CONFLICT (region, sku) DO UPDATE
... """)
```

**Important:** The conflict key columns must match the first N columns in the INSERT column list (in order). This is required because Rayforce uses positional key columns.

**Note:** UPSERT returns a new table with the changes applied. The original table is not mutated. `ON CONFLICT DO NOTHING` is not supported.

## SQL over IPC

Send SQL queries to a remote Rayforce server using the `SQLQuery` class:

```python
from rayforce import TCPClient
from rayforce.plugins.sql import SQLQuery

# Connect to remote server
client = TCPClient(host="localhost", port=5000)

# Execute SQL query on remote table
query = SQLQuery("employees", "SELECT dept, AVG(salary) FROM self GROUP BY dept")
result = client.execute(query)

# All SQL operations are supported
update_query = SQLQuery("employees", "UPDATE self SET salary = salary * 1.1 WHERE rating > 4")
client.execute(update_query)

insert_query = SQLQuery("employees", "INSERT INTO self (id, name) VALUES (100, 'New Hire')")
client.execute(insert_query)

upsert_query = SQLQuery("employees", """
    INSERT INTO self (id, name, salary)
    VALUES (100, 'Updated', 75000)
    ON CONFLICT (id) DO UPDATE
""")
client.execute(upsert_query)
```

The `SQLQuery` class parses the SQL on the client side and sends the compiled query to the server for execution. This provides the same functionality as `Table.sql()` but for remote tables.

## Limitations

The current SQL implementation supports common query patterns but has some limitations:

- `DELETE` statements are not supported
- `JOIN` operations are not yet supported via SQL (use the native `.inner_join()`, `.left_join()` methods)
- Subqueries are not supported
- `HAVING` clause is not supported
- `LIMIT` and `OFFSET` are not supported (use `.take()` on the result)

For complex operations not supported by SQL, use the native Rayforce query API which provides full functionality.
