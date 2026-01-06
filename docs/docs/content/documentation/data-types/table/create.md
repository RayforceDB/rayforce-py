# :material-table-plus: Creating a Table

Rayforce-Py provides several methods to create a [:octicons-table-24: Table](overview.md) instance.

## :fontawesome-solid-file-csv: From CSV file

Create a `Table` from a CSV file by specifying column types and the file path.

```python
>>> from rayforce import Table, I64, Timestamp, B8
>>> Table.from_csv(
        column_types=[I64, Timestamp, I64, B8],
        path="path_to_your_file.csv",
    )
```
!!! note ""
    **column_types** : `list[rayforce.Object]`:
        A list of Rayforce type objects that define the data types for each column in the CSV file. The order must match the column order in the CSV file. Each element should be a Rayforce type class such as `I64`, `F64`, `Timestamp`, `B8`, `String` etc...

    **path** : `str`:
        The file system path to the CSV file to be loaded. Can be a relative or absolute path.


## :material-code-braces: From Python Dictionary

Create a `Table` from a Python dictionary where keys are column names and values are Vectors of column data.

```python
>>> from rayforce import Table, Vector, I64, F64, Symbol
>>> table = Table(
        {
            "id": Vector([1, 2, 3, 4], ray_type=I64),
            "name": Vector(["Alice", "Bob", "Charlie", "Diana"], ray_type=Symbol),
            "score": Vector([95.5, 87.0, 92.5, 88.5], ray_type=F64),
        },
    )
```

!!! note ""
    **data** : `dict[str, list[Any]]`:
        A dictionary mapping column names (strings) to lists of values. All lists must have the same length, as they represent rows of data. The dictionary keys become the table column names.
