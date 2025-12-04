# :octicons-sort-desc-24: Order By Queries

You can sort the table using the following approach:

### XASC sorting
```python
>>> result = table.xasc("salary")
```

## XDESC sorting
```python
>>> result = table.xdesc("salary")
```

## Sort by multiple columns
```python
>>> result = table.xdesc("name", "salary")
```
