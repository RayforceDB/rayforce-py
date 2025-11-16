# WHERE Conditions

The `where()` method filters rows based on conditions. You can chain multiple `where()` calls or use complex boolean logic.

## Single Condition

Filter rows with a simple condition:

```python
result = table.select("id", "name").where(table.age >= 35).execute()
```

## Multiple WHERE Clauses

Chain multiple `where()` calls (they are combined with AND):

```python
result = (
    table.select("id", "name", "age", "salary")
    .where(table.age >= 35)
    .where(table.dept == "eng")
    .execute()
)
```

## Complex Boolean Logic

Use `&` (AND) and `|` (OR) operators for complex conditions:

```python
result = (
    table.select("id", "name")
    .where((table.age >= 35) & (table.dept == "eng"))
    .execute()
)
```

## Comparison Operators

RayPy supports all standard comparison operators:

- `==` - Equal to
- `!=` - Not equal to
- `>` - Greater than
- `>=` - Greater than or equal to
- `<` - Less than
- `<=` - Less than or equal to

## IN Operator

Check if a value is in a list:

```python
result = table.where(table.dept.isin(["eng", "marketing"])).execute()
```

