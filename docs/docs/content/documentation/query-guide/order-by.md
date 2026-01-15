# :octicons-sort-desc-24: Order By Queries

You can sort the table using the following approach:

### Ascending sort
```python
>>> result = table.sort_asc("salary")
```

## Descending sort
```python
>>> result = table.sort_desc("salary")
```

## Sort by multiple columns
```python
>>> result = table.sort_desc("name", "salary")
```
