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

Create a `Table` from a Python dictionary where keys are column names and values are lists of column data.

```python
>>> from rayforce import Table
>>> table = Table.from_dict(
        data={
            "id": [1, 2, 3, 4],
            "name": ["Alice", "Bob", "Charlie", "Diana"],
            "score": [95.5, 87.0, 92.5, 88.5]
        },
    )
```

!!! note ""
    **data** : `dict[str, list[Any]]`: 
        A dictionary mapping column names (strings) to lists of values. All lists must have the same length, as they represent rows of data. The dictionary keys become the table column names.


## :material-crane: Using Table Constructor

Create a `Table` directly by providing column names and values.

```python
>>> from rayforce import Table
>>> table = Table(
        columns=["id", "name", "active"],
        values=[
            [1, 2, 3, 4],
            ["Alice", "Bob", "Charlie", "Diana"],
            [True, False, True, False]
        ]
    )
```

!!! note ""
    **columns** : `list[str]`: 
        A list of column names (strings) for the new table.

    **values** : `list[list[Any]]`; 
        A list of column data, where each element is a list representing one column's values. Must have the same length as `columns`. <b>All inner lists has to be of the same length</b>.
