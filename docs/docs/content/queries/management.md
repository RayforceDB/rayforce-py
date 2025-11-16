# Table Management

## Saving Tables

Save a table to the database with a name:

```python
table.save("my_table_name")
```

Once saved, you can reference the table by name in future operations.

## Loading Tables

Load a previously saved table:

```python
table = Table.get("my_table_name")
```

## Getting Table Information

Access table metadata:

```python
# Get column names
columns = table.columns
# Returns: ["id", "name", "age", "salary"]

# Get table shape (rows, columns)
shape = table.shape
# Returns: (4, 4)

# Get number of rows
row_count = len(table)
# Returns: 4

# Get table values
values = table.values()
# Returns a list of column vectors
```

## Concatenating Tables

Combine multiple tables:

```python
table1 = Table(...)
table2 = Table(...)
table3 = Table(...)

# Concatenate two tables
combined = table1.concat(table2)

# Concatenate multiple tables
combined = table1.concat(table2, table3)

# Or use the static method
combined = Table.concat_all([table1, table2, table3])
```

