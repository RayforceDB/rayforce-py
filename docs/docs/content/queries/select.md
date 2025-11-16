# SELECT Queries

The `select()` method allows you to choose which columns to retrieve from a table. You can select specific columns or compute new ones.

## Basic Selection

Select specific columns:

```python
result = table.select("id", "name", "age").execute()
```

## Selecting All Columns

To select all columns, you can use `"*"`:

```python
result = table.select("*").execute()
```

## Computed Columns

You can create computed columns using expressions:

```python
result = table.select(
    "id",
    total=table.price * table.quantity,
).execute()
```

The computed columns are named using keyword arguments, where the key is the column name and the value is the expression.

## Combining with WHERE

SELECT queries are often combined with WHERE conditions:

```python
result = table.select("id", "name", "age").where(table.age >= 35).execute()
```
