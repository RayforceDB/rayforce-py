# :octicons-plus-24: Table Joins

Rayforce-Py provides a useful interface to the Rayforce table joins.

!!! warning ""
    Join operations work without lazy-loading, and performed without `.execute()` statement.

## :material-border-inside: Inner Join

Inner join combines two tables based on matching values in specified columns. Only rows with matching keys in both tables are included in the result.

```python
>>> from rayforce import Table, Vector, Symbol, Time, I64, F64

>>> trades = Table.from_dict({
        "sym": Vector(items=["AAPL", "AAPL", "GOOG", "GOOG"], ray_type=Symbol),
        "time": Vector(
            items=[
                Time("09:00:00.100"),
                Time("09:00:00.200"),
                Time("09:00:00.150"),
                Time("09:00:00.250"),
            ],
            ray_type=Time,
        ),
        "price": Vector(items=[100, 200, 300, 400], ray_type=I64),
    })

>>> quotes = Table.from_dict({
        "sym": Vector(items=["AAPL", "GOOG"], ray_type=Symbol),
        "bid": Vector(items=[50, 100], ray_type=I64),
        "ask": Vector(items=[75, 150], ray_type=I64),
    })

>>> result = trades.inner_join(quotes, on="sym")
┌──────┬──────────────┬───────┬─────┬─────┐
│ sym  │ time         │ price │ bid │ ask │
├──────┼──────────────┼───────┼─────┼─────┤
│ AAPL │ 09:00:00.100 │ 100   │ 50  │ 75  │
│ AAPL │ 09:00:00.100 │ 100   │ 50  │ 75  │
│ GOOG │ 09:00:00.200 │ 200   │ 100 │ 150 │
│ GOOG │ 09:00:00.200 │ 200   │ 100 │ 150 │
├──────┴──────────────┴───────┴─────┴─────┤
│ 4 rows (4 shown) 5 columns (5 shown)    │
└─────────────────────────────────────────┘
```

!!! note ""
    If you wish to join on multiple columns, provide a list of strings


## :material-arrow-left: Left Join

Left join returns all rows from the left table and matching rows from the right table. If there's no match, the right table columns will have null values.

```python
>>> from rayforce import Table, Vector, Symbol, Time, I64, F64

>>> trades = Table.from_dict({
        "sym": Vector(items=["AAPL", "MSFT", "GOOG"], ray_type=Symbol),
        "time": Vector(
            items=[
                Time("09:00:00.100"),
                Time("09:00:00.200"),
                Time("09:00:00.150"),
            ],
            ray_type=Time,
        ),
        "price": Vector(items=[100, 200, 300], ray_type=I64),
    })

>>> quotes = Table.from_dict({
        "sym": Vector(items=["AAPL", "GOOG"], ray_type=Symbol),
        "bid": Vector(items=[50, 100], ray_type=I64),
        "ask": Vector(items=[75, 150], ray_type=I64),
    })

>>> result = trades.left_join(quotes, on="sym")
```

!!! note ""
    If you wish to join on multiple columns, provide a list of strings:
    ```python
    result = trades.left_join(quotes, on=["col1", "col2"])
    ```

## :material-window-maximize: Window Join

Window join matches records on specified columns and aggregates values from another table within time windows. This is useful for financial data where you want to aggregate quotes that occurred near each trade.

```python
>>> from rayforce import Table, TableColumnInterval, Vector, Symbol, Time, F64

>>> trades = Table.from_dict({
        "sym": Vector(items=["AAPL", "GOOG"], ray_type=Symbol),
        "time": Vector(
            items=[Time("09:00:00.100"), Time("09:00:00.100")],
            ray_type=Time,
        ),
        "price": Vector(items=[150.0, 200.0], ray_type=F64),
    })

>>> quotes = Table.from_dict({
        "sym": Vector(items=["AAPL", "AAPL", "AAPL", "GOOG", "GOOG", "GOOG"], ray_type=Symbol),
        "time": Vector(
            items=[
                Time("09:00:00.090"),
                Time("09:00:00.095"),
                Time("09:00:00.105"),
                Time("09:00:00.090"),
                Time("09:00:00.095"),
                Time("09:00:00.105"),
            ],
            ray_type=Time,
        ),
        "bid": Vector(items=[99.0, 100.0, 101.0, 199.0, 200.0, 201.0], ray_type=F64),
        "ask": Vector(items=[109.0, 110.0, 111.0, 209.0, 210.0, 211.0], ray_type=F64),
    })

>>> interval = TableColumnInterval(
        lower=-10,
        upper=10,
        table=trades,
        column=Column("time"),
    )

>>> result = trades.window_join(
        on=["sym", "time"],
        interval=interval,
        join_with=[quotes],
        min_bid=Column("bid").min(),
        max_ask=Column("ask").max(),
    )
┌──────┬──────────────┬────────┬─────────┬─────────┐
│ sym  │ time         │ price  │ min_bid │ max_ask │
├──────┼──────────────┼────────┼─────────┼─────────┤
│ AAPL │ 09:00:00.100 │ 150.00 │ 99.00   │ 111.00  │
│ GOOG │ 09:00:00.100 │ 200.00 │ 199.00  │ 211.00  │
└──────┴──────────────┴────────┴─────────┴─────────┘
```
!!! note ""
    For the AAPL trade at `09:00:00.100`, the window `[090ms, 110ms]` captures quotes at 90ms, 95ms, and 105ms, aggregating them to find `min_bid=99.0` and `max_ask=111.0`.

### :grey_question: Window Join vs Window Join 1

- `window_join()`: Uses open intervals (excludes boundaries)
- `window_join1()`: Uses closed intervals (includes boundaries)

```python
# Open intervals - may exclude boundary values
result = trades.window_join(on=["sym", "time"], interval=interval, join_with=[quotes], ...)

# Closed intervals - includes boundary values  
result = trades.window_join1(on=["sym", "time"], interval=interval, join_with=[quotes], ...)
```
