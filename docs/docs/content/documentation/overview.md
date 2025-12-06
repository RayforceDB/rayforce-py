# :material-file-document: Start your journey here

Rayforce-Py allows you to operate with Rayforce runtime in a seamless manner, utilising handy
Pythonic chainable syntax with little-to-no performance overhead.

To achieve this, library provides instruments to operate with the runtime, along with data types and other handy things you may utilise on your way to fast performance when operating with the data!


## :material-run: Quick Start

Initialise a table using `rayforce.Table`:
```python
>>> from datetime import time
>>> from rayforce import Table, Vector, Symbol, Time, F64

>>> quotes = Table.from_dict({
        "symbol": Vector(items=["AAPL", "AAPL", "AAPL", "GOOG", "GOOG", "GOOG"], ray_type=Symbol),
        "time": Vector(
            items=[
                time.fromisoformat("09:00:00.095"),
                time.fromisoformat("09:00:00.105"),
                time.fromisoformat("09:00:00.295"),
                time.fromisoformat("09:00:00.145"),
                time.fromisoformat("09:00:00.155"),
                time.fromisoformat("09:00:00.345"),
            ],
            ray_type=Time,
        ),
        "bid": Vector(items=[100.0, 101.0, 102.0, 200.0, 201.0, 202.0], ray_type=F64),
        "ask": Vector(items=[110.0, 111.0, 112.0, 210.0, 211.0, 212.0], ray_type=F64),
    })
```
!!! note ""
    You are able to initialize table in multiple handy ways. See [:material-table-plus: Create a Table](./data-types/table/create.md)

Then, query the table using `select` statement:
```python
>>> result = (
    quotes
    .select(
        max_bid=Column("bid").max(),
        min_bid=Column("bid").min(),
        avg_ask=Column("ask").mean(),
        records_count=Column("time").count(),
        first_bid=Column("time").first(),
    )
    .by("symbol")
    .execute()
)
>>> print(result)
┌────────┬─────────┬─────────┬─────────┬───────────────┬──────────────┐
│ symbol │ max_bid │ min_bid │ avg_ask │ records_count │ first_bid    │
├────────┼─────────┼─────────┼─────────┼───────────────┼──────────────┤
│ AAPL   │ 102.00  │ 100.00  │ 111.00  │ 3             │ 09:00:00.095 │
│ GOOG   │ 202.00  │ 200.00  │ 211.00  │ 3             │ 09:00:00.145 │
├────────┴─────────┴─────────┴─────────┴───────────────┴──────────────┤
│ 2 rows (2 shown) 6 columns (6 shown)                                │
└─────────────────────────────────────────────────────────────────────┘
```
Try it out!

### :material-arrow-right: Next: Discover [:octicons-database-16: Data Types](./data-types/overview.md) and [:material-database-eye-outline: Query Guide](./query-guide/overview.md)
