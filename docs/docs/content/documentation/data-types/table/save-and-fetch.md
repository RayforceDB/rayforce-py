# :material-content-save: Save and Fetch Table

<b>This is a work in progress section.</b>

Rayforce-Py gives you access to safely save a table behind a Rayforce environment variable and fetch it.

```python
>>> table: Table
>>> table.save("mytable")

>>> Table.get("mytable").select("*").execute()

# TODO: figure out how to safely fetch a table without select statement
```

