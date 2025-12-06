# :material-content-save: Save and Fetch Table


Rayforce-Py gives you access to safely save a table behind a Rayforce environment variable and fetch it.

```python
>>> table: Table
>>> table.save("mytable")

>>> Table.from_name("mytable")
TableReference['mytable']  # This is unfeched prepared state, and table has to be selected from database

>>> Table.from_name("mytable").columns()
Vector([Symbol('symbol'), Symbol('time'), Symbol('bid'), Symbol('ask')])

>>> Table.from_name("mytable").values()
List([Vector ...])  # collapsed in documentation for convenience

>>> Table.from_name("mytable").select("*").execute()
Table[Symbol('symbol'), Symbol('time'), Symbol('bid'), Symbol('ask')]

>>> Table.from_name("test").select("time").execute()
Table[Symbol('time')]
```

