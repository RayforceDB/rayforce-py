# Table

The `Table` type represents a structured data table. It consists of named columns and rows of data.


### Creating Table Values

```python
from rayforce import Table

# Create table with columns and data
columns = ["id", "name", "age", "salary"]
values = [
    [1, 2, 3, 4, 5],                                    # id column
    ["Alice", "Bob", "Charlie", "Diana", "Eve"],        # name column  
    [25, 30, 35, 28, 32],                              # age column
    [50000, 60000, 70000, 55000, 65000]                # salary column
]

employee_table = Table(columns=columns, values=values)
```

### Accessing Table Data

```python
# Get column names
columns = employee_table.columns()
print(f"Columns: {[col.value for col in columns]}")

# Get all data
data = employee_table.values()
print(f"Data: {[row for row in data]}")
```

## Notes

- Tables represent structured, columnar data with named columns
- All columns should have the same number of rows for consistency
- Use `.columns()` to get a vector of column names
- Use `.values()` to get a list containing each column's data
