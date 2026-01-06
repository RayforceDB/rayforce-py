# :material-content-save: Save and Fetch Table


Rayforce-Py gives you access to safely save a table behind a Rayforce environment variable and fetch it.

```python
>>> table: Table
>>> table.save("mytable")

>>> Table("mytable")
TableReference['mytable']  # This is unfeched prepared state, and table has to be selected from database

>>> Table("mytable").columns()
Vector([Symbol('symbol'), Symbol('time'), Symbol('bid'), Symbol('ask')])

>>> Table("mytable").values()
List([Vector ...])  # collapsed in documentation for convenience

>>> Table("mytable").select("*").execute()
Table[Symbol('symbol'), Symbol('time'), Symbol('bid'), Symbol('ask')]

>>> Table("test").select("time").execute()
Table[Symbol('time')]
```
