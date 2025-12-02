# ⚡ High-Performance Python Interface for [RayforceDB](https://github.com/RayforceDB/rayforce)

![Documentation](https://img.shields.io/website?url=https%3A%2F%2Fraypy.rayforcedb.com%2F) [![Tests](https://img.shields.io/badge/Tests-passing-success?logo=github&style=flat)](soon) [![Coverage](https://img.shields.io/badge/Coverage-passing-brightgreen?style=flat&logo=github)](soon) [![Release](https://img.shields.io/github/v/release/RayforceDB/rayforce-py)](https://github.com/RayforceDB/rayforce-py/releases)
![Python Version](https://img.shields.io/pypi/pyversions/rayforce-py.svg)


## Features

- **Pythonic API** - Chainable, fluent query syntax that feels pythonic
- **High Performance** - Minimal overhead between Python and RayforceDB runtime thanks to C API usage
- **Active Development** - Continuously expanding functionality


## 📦 Installation

Package is available on [Pypi](https://pypi.org/project/rayforce-py/0.0.5/)
```bash
pip install rayforce-py
```

## 🚀 Quick Start

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

>>> result = (
        quotes
        .select(
            max_bid=quotes.bid.max(),
            min_bid=quotes.bid.min(),
            avg_ask=quotes.ask.mean(),
            records_count=quotes.time.count(),
            first_bid=quotes.time.first(),
        )
        .where((quotes.bid >= 110) & (quotes.ask > 100))
        .by("symbol")
        .execute()
    )
>>> print(result)
┌────────┬─────────┬─────────┬─────────┬───────────────┬──────────────┐
│ symbol │ max_bid │ min_bid │ avg_ask │ records_count │ first_bid    │
├────────┼─────────┼─────────┼─────────┼───────────────┼──────────────┤
│ GOOG   │ 202.00  │ 200.00  │ 211.00  │ 3             │ 09:00:00.145 │
├────────┴─────────┴─────────┴─────────┴───────────────┴──────────────┤
│ 1 rows (1 shown) 6 columns (6 shown)                                │
└─────────────────────────────────────────────────────────────────────┘
```

**Full documentation available at:** https://raypy.rayforcedb.com/

---

**Built with ❤️ for high-performance data processing**
