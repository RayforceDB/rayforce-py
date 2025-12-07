# :material-view-column: Set Splayed

In Rayforce-Py, you can set a table splayed to the disk. 


### Usage
```python
>>> table.set_splayed("path/to/directory/")  # Trailing slash is required
# Folder and files gets created

>>> from_splayed = Table.from_splayed("./tables/test/")
>>> print(from_splayed)
┌────────┬──────────┬─────────────────────────┐
│ id     │ value    │ label                   │
├────────┼──────────┼─────────────────────────┤
│ 0      │ 0.00     │ item_0                  │
│ 1      │ 1.50     │ item_1                  │
│ 2      │ 3.00     │ item_2                  │
```

