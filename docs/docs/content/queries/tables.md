# Creating Tables

Before you can query data, you need to create a table. RayPy provides several ways to create tables:

## From Columns and Values

The most straightforward way is to provide columns and values as lists:

```python
from rayforce import Table

table = Table(
    columns=["id", "name", "age", "salary", "dept"],
    values=[
        ["001", "002", "003", "004"],
        ["alice", "bob", "charlie", "dana"],
        [29, 34, 41, 38],
        [100000, 120000, 90000, 85000],
        ["eng", "sales", "field", "market"],
    ],
)
```

## From Dictionary

You can create a table from a dictionary where keys are column names:

```python
table = Table.from_dict({
    "id": ["001", "002", "003"],
    "name": ["alice", "bob", "charlie"],
    "age": [29, 34, 41],
})
```

## From Records

Create a table from a list of dictionaries (records):

```python
table = Table.from_records([
    {"id": "001", "name": "alice", "age": 29},
    {"id": "002", "name": "bob", "age": 34},
    {"id": "003", "name": "charlie", "age": 41},
])
```

## Loading Existing Tables

If you've saved a table previously, you can load it by name:

```python
table = Table.get("my_saved_table")
```

