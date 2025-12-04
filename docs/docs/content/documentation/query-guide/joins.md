# :octicons-plus-24: Table Joins

Rayforce-Py provides a useful interface to the Rayforce table joins.

!!! warning ""
    Join operations work without lazy-loading, and performed without `.execute()` statement.

## :material-border-inside: Inner Join

Inner join combines two tables based on matching values in specified columns. Only rows with matching keys in both tables are included in the result.

```python
>>> trades = Table(
        columns=["sym", "time", "price"],
        values=[
            ["AAPL", "AAPL", "GOOG", "GOOG"],
            [Time("09:00:00.100"), Time("09:00:00.200"), Time("09:00:00.150"), Time("09:00:00.250")],
            [100, 200, 300, 400],
        ],
    )

>>> quotes = Table(
        columns=["sym", "bid", "ask"],
        values=[
            ["AAPL", "GOOG"],
            [50, 100],
            [75, 150],
        ],
    )

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
```python
result = trades.left_join(quotes, on=["col1", "col2"])
```

## :material-window-maximize: Window Join

Window join matches records on specified columns and aggregates values from another table within time windows. This is useful for financial data where you want to aggregate quotes that occurred near each trade.

```python
>>> from rayforce import TableColumnInterval
>>> trades = Table(
        columns=["sym", "time", "price"],
        values=[
            ["AAPL", "GOOG"],
            [Time("09:00:00.100"), Time("09:00:00.100")],
            [150.0, 200.0],
        ],
    )

>>> quotes = Table(
        columns=["sym", "time", "bid", "ask"],
        values=[
            ["AAPL", "AAPL", "AAPL", "GOOG", "GOOG", "GOOG"],
            [
                Time("09:00:00.090"), Time("09:00:00.095"),
                Time("09:00:00.105"), Time("09:00:00.090"),
                Time("09:00:00.095"), Time("09:00:00.105"),
            ],
            [99.0, 100.0, 101.0, 199.0, 200.0, 201.0],
            [109.0, 110.0, 111.0, 209.0, 210.0, 211.0],
        ],
    )

>>> interval = TableColumnInterval(
        lower=-10,
        upper=10,
        table=trades,
        column=trades.time,
    )

>>> result = trades.window_join(
        on=["sym", "time"],
        interval=interval,
        join_with=[quotes],
        min_bid=quotes.bid.min(),
        max_ask=quotes.ask.max(),
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
