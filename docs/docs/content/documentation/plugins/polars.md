# :fontawesome-solid-table: Polars DataFrame Integration

<b>This functionality is in Alpha and may behave unexpectedly</b>

Rayforce-Py provides seamless conversion from Polars DataFrames to Rayforce-Py [:octicons-table-24: Tables](../data-types/table/overview.md )

## Installation

The polars integration is available as an optional dependency. Install it with:

```bash
pip install rayforce-py[polars]
```

## Basic Usage

To convert a Polars DataFrame to a Rayforce Table, import the `from_polars` function:

```python
>>> import polars as pl
>>> from rayforce.plugins.polars import from_polars

>>> df = pl.DataFrame({
...     "id": [1, 2, 3, 4, 5],
...     "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
...     "age": [25, 30, 35, 28, 32],
...     "salary": [50000.0, 60000.0, 70000.0, 55000.0, 65000.0],
...     "active": [True, True, False, True, False],
... })

>>> table = from_polars(df)
>>> table
Table(columns=['id', 'name', 'age', 'salary', 'active'])

>>> print(table)
┌────┬─────────┬─────┬──────────┬────────┐
│ id │ name    │ age │ salary   │ active │
├────┼─────────┼─────┼──────────┼────────┤
│ 1  │ Alice   │ 25  │ 50000.0  │ true   │
│ 2  │ Bob     │ 30  │ 60000.0  │ true   │
│ 3  │ Charlie │ 35  │ 70000.0  │ false  │
│ 4  │ Diana   │ 28  │ 55000.0  │ true   │
│ 5  │ Eve     │ 32  │ 65000.0  │ false  │
├────┴─────────┴─────┴──────────┴────────┘
│ 5 rows (5 shown) 5 columns (5 shown)   │
└────────────────────────────────────────┘
```

## Type Conversion

The `from_polars()` function automatically infers Rayforce types from Polars dtypes:

| Polars dtype | Rayforce Type |
|--------------|---------------|
| `Int8`, `Int16` | `I16` |
| `Int32` | `I32` |
| `Int64` | `I64` |
| `Float32`, `Float64` | `F64` |
| `Boolean` | `B8` |
| `String`, `Utf8` | `Symbol` |
| `Date` | `Date` |
| `Datetime` | `Timestamp` |
