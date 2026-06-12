# :material-table-pivot: Pivot

Reshape data from long to wide format using `.pivot()`

!!! note ""
    Pivot creates a spreadsheet-style pivot table where unique values from one column become new column headers, and values are aggregated.

Transform data where each unique value in the `columns` parameter becomes a new column:

```python
>>> from rayforce import Table, Vector, Symbol, I64

>>> table = Table({
        "symbol": Vector(items=["AAPL", "AAPL", "GOOG", "GOOG"], ray_type=Symbol),
        "metric": Vector(items=["price", "volume", "price", "volume"], ray_type=Symbol),
        "value": Vector(items=[150, 1000, 2800, 500], ray_type=I64),
    })

>>> result = table.pivot(index="symbol", columns="metric", values="value").execute()
┌────────┬───────┬────────────────────┐
│ symbol │ price │       volume       │
│  SYM   │  I64  │        I64         │
├────────┼───────┼────────────────────┤
│ AAPL   │ 150   │ 1000               │
│ GOOG   │ 2800  │ 500                │
├────────┴───────┴────────────────────┤
│ 2 rows (2 shown) 3 columns (3 shown)│
└─────────────────────────────────────┘
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `index` | `str` or `list[str]` | Column(s) to use as the row index |
| `columns` | `str` | Column whose unique values become new column headers |
| `values` | `str` | Column containing values to aggregate |
| `aggfunc` | `str` | Aggregation function (default: `"min"`) |

## Multiple Index Columns

Group by multiple columns by passing a list to `index`:

```python
>>> table = Table({
        "date": Vector(items=["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"], ray_type=Symbol),
        "symbol": Vector(items=["AAPL", "AAPL", "AAPL", "AAPL"], ray_type=Symbol),
        "metric": Vector(items=["open", "close", "open", "close"], ray_type=Symbol),
        "value": Vector(items=[150, 152, 153, 155], ray_type=I64),
    })

>>> result = table.pivot(index=["date", "symbol"], columns="metric", values="value").execute()
┌────────────┬────────┬──────┬────────┐
│    date    │ symbol │ open │ close  │
│    SYM     │  SYM   │ I64  │  I64   │
├────────────┼────────┼──────┼────────┤
│ 2024-01-01 │ AAPL   │ 150  │ 152    │
│ 2024-01-02 │ AAPL   │ 153  │ 155    │
├────────────┴────────┴──────┴────────┤
│ 2 rows (2 shown) 4 columns (4 shown)│
└─────────────────────────────────────┘
```

## Aggregation Functions

When multiple values exist for the same index/column combination, use `aggfunc` to specify how to aggregate them:

| Function | Description |
|----------|-------------|
| `"min"` | Minimum value (default) |
| `"max"` | Maximum value |
| `"sum"` | Sum of values |
| `"count"` | Count of values |
| `"avg"` | Average (mean) of values |
| `"first"` | First value encountered |
| `"last"` | Last value encountered |
