# :fontawesome-solid-table: Pandas DataFrame Integration

<b>This functionality is in Alpha and may behave unexpectedly</b>

Rayforce-Py provides seamless conversion from Pandas DataFrames to Rayforce-Py [:octicons-table-24: Tables](../data-types/table/overview.md )

## Installation

The pandas integration is available as an optional dependency. Install it with:

```bash
pip install rayforce-py[pandas]
```

## Basic Usage

To convert a Pandas DataFrame to a Rayforce Table, import the `from_pandas` function:

```python
>>> import pandas as pd
>>> from rayforce.plugins.pandas import from_pandas

>>> df = pd.DataFrame({
...     "id": [1, 2, 3, 4, 5],
...     "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
...     "age": [25, 30, 35, 28, 32],
...     "salary": [50000.0, 60000.0, 70000.0, 55000.0, 65000.0],
...     "active": [True, True, False, True, False],
... })

>>> table = from_pandas(df)
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

The `from_pandas()` function automatically infers Rayforce types from Pandas dtypes:

| Pandas dtype | Rayforce Type |
|--------------|---------------|
| `int8`, `int16` | `I16` |
| `int32`, `int` | `I32` |
| `int64`, `int_` | `I64` |
| `float32`, `float`, `float64` | `F64` |
| `bool`, `boolean`, `bool8` | `B8` |
| `object`, `string`, `str` | `Symbol` |
| `date` (object dtype with date objects) | `Date` |
| `datetime64[ns]`, `datetime64` | `Timestamp` |
