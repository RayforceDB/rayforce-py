# :material-view-column: Set Splayed

In Rayforce-Py, you can set a table splayed to the disk and load it back.

## Setting a Table Splayed

```python
>>> table.set_splayed(path="path/to/directory/")
# Folder and files gets created
```
!!! note ""
    - `path` (str): Path where to store the table. (has to be directory with `/`)
    - `symlink` (str, optional): Path to a symlink file if the table uses symbolic links. (if parted table access is required)

!!! note ""
    When you set a table splayed, each column is saved as a separate file in the specified directory. The directory will contain
    `.d` file (metadata) and one file per column (named after the column)

    Optionally - a `sym` file gets created as well.

## Loading a Splayed Table
```python
>>> table = Table.from_splayed("path/to/directory/")
>>> table.columns()
[Symbol('category'), Symbol('amount'), Symbol('status')]

>>> result = table.select("*").execute()
>>> result.values()
...
```
!!! warning ""
    Splayed tables require using `.select()` before accessing values. Direct access to `.values()` will raise a `PartedTableError`.

!!! note ""
    - `path` (str): Path to the directory containing the splayed table.
    - `symlink` (str, optional): Path to a symlink file if the table uses symbolic links.

## Loading a Parted Table
```python
>>> # First, set multiple splayed tables with a symlink
>>> table.set_splayed("./db/2024.01.01/data/", "./db/sym")
>>> table.set_splayed("./db/2024.01.02/data/", "./db/sym")
>>> table.set_splayed("./db/2024.01.03/data/", "./db/sym")

>>> parted_table = Table.from_parted("./db/", "data")
>>> parted_table.columns()
[Symbol('Date'), Symbol('category'), Symbol('amount'), Symbol('status')]

>>> result = parted_table.select("*").execute()
>>> result.values()
...
```
!!! note ""
    - `path` (str): Base path to the directory containing partitioned subdirectories.
    - `symlink` (str): The symlink name used when setting the splayed tables. This identifies which subdirectories belong to this parted table.

Parted tables automatically include a `Date` column representing the partition date. Like splayed tables, you must use `.select()` before accessing values.
