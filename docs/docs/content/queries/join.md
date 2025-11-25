# Join Operations

## Inner Join

Inner join combines two tables based on matching values in specified columns. Only rows with matching keys in both tables are included in the result.

```python
# Create two tables
trades = Table(
    columns=["sym", "time", "price"],
    values=[
        ["AAPL", "AAPL", "GOOG", "GOOG"],
        [Time("09:00:00.100"), Time("09:00:00.200"), Time("09:00:00.150"), Time("09:00:00.250")],
        [100, 200, 300, 400],
    ],
)

quotes = Table(
    columns=["sym", "bid", "ask"],
    values=[
        ["AAPL", "GOOG"],
        [50, 100],
        [75, 150],
    ],
)

# Join on symbol column
result = trades.inner_join(quotes, on="sym")
```

**Result:**
```
┌──────┬──────────────┬────────┬─────┬─────┐
│ sym  │ time         │ price  │ bid │ ask │
├──────┼──────────────┼────────┼─────┼─────┤
│ AAPL │ 09:00:00.100 │ 100    │ 50  │ 75  │
│ AAPL │ 09:00:00.200 │ 200    │ 50  │ 75  │
│ GOOG │ 09:00:00.150 │ 300    │ 100 │ 150 │
│ GOOG │ 09:00:00.250 │ 400    │ 100 │ 150 │
└──────┴──────────────┴────────┴─────┴─────┘
```

### Join on Multiple Columns

```python
result = table1.inner_join(table2, on=["col1", "col2"])
```

## Window Join

Window join matches records on specified columns and aggregates values from another table within time windows. This is useful for financial data where you want to aggregate quotes that occurred near each trade.

### Basic Example

```python
# Trades at specific times
trades = Table(
    columns=["sym", "time", "price"],
    values=[
        ["AAPL", "GOOG"],
        [Time("09:00:00.100"), Time("09:00:00.100")],
        [150.0, 200.0],
    ],
)

# Quotes at various times
quotes = Table(
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

# Define time window: ±10ms around each trade
interval = TableColumnInterval(
    lower=-10,
    upper=10,
    table=trades,
    column=trades.time,
)

# Perform window join with aggregations
result = trades.window_join(
    on=["sym", "time"],
    interval=interval,
    join_with=[quotes],
    min_bid=quotes.bid.min(),
    max_ask=quotes.ask.max(),
)
```

**Result:**
```
┌──────┬──────────────┬────────┬─────────┬─────────┐
│ sym  │ time         │ price  │ min_bid │ max_ask │
├──────┼──────────────┼────────┼─────────┼─────────┤
│ AAPL │ 09:00:00.100 │ 150.00 │ 99.00   │ 111.00  │
│ GOOG │ 09:00:00.100 │ 200.00 │ 199.00  │ 211.00  │
└──────┴──────────────┴────────┴─────────┴─────────┘
```

For the AAPL trade at `09:00:00.100`, the window `[090ms, 110ms]` captures quotes at 90ms, 95ms, and 105ms, aggregating them to find `min_bid=99.0` and `max_ask=111.0`.

### Window Join vs Window Join1

- `window_join()`: Uses open intervals (excludes boundaries)
- `window_join1()`: Uses closed intervals (includes boundaries)

```python
# Open intervals - may exclude boundary values
result = trades.window_join(on=["sym", "time"], interval=interval, join_with=[quotes], ...)

# Closed intervals - includes boundary values  
result = trades.window_join1(on=["sym", "time"], interval=interval, join_with=[quotes], ...)
```
