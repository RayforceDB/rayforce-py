# JOIN Operations

Join two tables together using the `join()` method.

## Inner Join

Perform an inner join on one or more columns:

```python
table1 = Table(columns=["id", "name"], values=[...])
table2 = Table(columns=["id", "department"], values=[...])

result = table1.join(table2, on="id", how="inner")
```

## Multiple Join Keys

Join on multiple columns:

```python
result = table1.join(table2, on=["id", "version"], how="inner")
```

## Using `inner_join()` Method

For convenience, you can use the `inner_join()` method:

```python
result = table1.inner_join(table2, on="id")
```
