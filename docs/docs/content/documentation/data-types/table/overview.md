# :octicons-table-24: Table

The `Table` type represents a structured data table. It consists of columns and rows of data.

```python
>>> from rayforce import Table

>>> columns = ["id", "name", "age", "salary"]
>>> values = [
        [1, 2, 3, 4, 5],                                   # id column
        ["Alice", "Bob", "Charlie", "Diana", "Eve"],       # name column  
        [25, 30, 35, 28, 32],                              # age column
        [50000, 60000, 70000, 55000, 65000]                # salary column
    ]

>>> employee_table = Table(columns=columns, values=values)
>>> employee_table
Table(columns=['id', 'name', 'age', 'salary'])

>>> print(employee_table)
┌────┬─────────┬─────┬─────────────────┐
│ id │ name    │ age │ salary          │
├────┼─────────┼─────┼─────────────────┤
│ 1  │ Alice   │ 25  │ 50000           │
│ 2  │ Bob     │ 30  │ 60000           │
│ 3  │ Charlie │ 35  │ 70000           │
│ 4  │ Diana   │ 28  │ 55000           │
│ 5  │ Eve     │ 32  │ 65000           │
├────┴─────────┴─────┴─────────────────┤
│ 5 rows (5 shown) 4 columns (4 shown) │
└──────────────────────────────────────┘
```

## :octicons-info-24: Details

Table columns object is a [:material-vector-line: Vector](../vector.md) of [:material-text: Symbols](../symbol.md). Due to QL restrictions, <b>column names can not contain spaces or tabulations</b>.

Table values object is a [:material-code-array: List](../list.md) of [:material-vector-line: Vectors](../vector.md) of specific type. Each Vector represents a specific column in table.

