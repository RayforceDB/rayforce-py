# :material-human-greeting-variant: Introduction to Rayforce-Py

Rayforce-Py is an library which allows you to effectively execute statements inside RayforceDB runtime using handy Pythonic syntax.

The interaction with the RayforceDB is happening via C API bus, which allows us to seamlessly operate with your local rayforce runtime with little-to-no practical overhead.

## Installation

Supported Python versions: `3.11`, `3.12`, `3.13`

### with pip (recommended)
Distribution is available via pypi for Linux and MacOS (Windows support is in progress):
```bash
python -m pip install rayforce-py
```

### from source
You can manually clone latest github repo and build it yourself
```zsh
~ $ git clone https://github.com/RayforceDB/rayforce-py.git
~ $ cd rayforce-py
~/rayforce-py $ make all
~/rayforce-py $ python -c "import rayforce; print(rayforce.version)"
0.0.3
```

This will:

- Pull the latest RayforceDB version from Github
- Build .so binaries specifically for your platform




## Making your first queries

Initialise a table using `rayforce.Table`:
```python
>>> from datetime import time
>>> from rayforce import Table

>>> quotes = Table(
    columns=["symbol", "time", "bid", "ask"],
    values=[
        ["AAPL", "AAPL", "AAPL", "GOOG", "GOOG", "GOOG"],
        [
            time.fromisoformat("09:00:00.095"),
            time.fromisoformat("09:00:00.105"),
            time.fromisoformat("09:00:00.295"),
            time.fromisoformat("09:00:00.145"),
            time.fromisoformat("09:00:00.155"),
            time.fromisoformat("09:00:00.345"),
        ],
        [100.0, 101.0, 102.0, 200.0, 201.0, 202.0],
        [110.0, 111.0, 112.0, 210.0, 211.0, 212.0],
    ],
)
```
You are able to initialize table in multiple ways. See [TODO]

## Example query
```python
>>> result = (
    quotes
    .select(
        max_bid=quotes.bid.max(),
        min_bid=quotes.bid.min(),
        avg_ask=quotes.ask.mean(),
        records_count=quotes.time.count(),
        first_bid=quotes.time.first(),
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

Discover the full queries potential in documentation!
