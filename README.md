<table style="border-collapse:collapse;border:0;">
  <tr>
    <td style="border:0;padding:0;">
      <a href="https://py.rayforcedb.com">
        <picture>
            <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/RayforceDB/rayforce-py/refs/heads/master/docs/docs/assets/py_logo_light.svg">
            <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/RayforceDB/rayforce-py/refs/heads/master/docs/docs/assets/py_logo_dark.svg">
            <img src="https://raw.githubusercontent.com/RayforceDB/rayforce-py/refs/heads/master/docs/docs/assets/py_logo_dark.svg" width="200">
        </picture>
      </a>
    </td>
    <td style="border:0;padding:0;">
      <h1>High-Performance Lightweight Python ORM designed for <a href="https://core.rayforcedb.com"><picture>
            <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/RayforceDB/rayforce-py/refs/heads/master/docs/docs/assets/logo_light_full.svg">
            <img src="https://raw.githubusercontent.com/RayforceDB/rayforce-py/refs/heads/master/docs/docs/assets/logo_dark_full.svg" alt="RayforceDB" height="40" style="vertical-align: bottom;">
        </picture></a></h1>
    </td>
  </tr>
</table>

![Documentation](https://img.shields.io/website?url=https%3A%2F%2Fpy.rayforcedb.com%2F) [![Tests](https://img.shields.io/badge/Tests-passing-success?logo=github&style=flat)](soon) [![Coverage](https://img.shields.io/badge/Coverage-passing-brightgreen?style=flat&logo=github)](soon) [![Release](https://img.shields.io/github/v/release/RayforceDB/rayforce-py)](https://github.com/RayforceDB/rayforce-py/releases)
![Python Version](https://img.shields.io/pypi/pyversions/rayforce-py.svg)

Python ORM for RayforceDB, a high-performance columnar database designed for analytics and data operations. Core is written in pure C with minimal overhead - combines columnar storage with SIMD vectorization for lightning-fast analytics on time-series and big data workloads.

**Full Documentation:** https://py.rayforcedb.com/

## Features

- **Pythonic API** - Chainable, fluent query syntax
- **High Performance** - Minimal overhead between Python and RayforceDB runtime via C API
- **Lightweight** - Core is less than 1 MB footprint
- **Active Development** - Continuously expanding functionality

![RayforcePy Benchmarks](https://raw.githubusercontent.com/RayforceDB/rayforce-py/refs/heads/master/docs/docs/assets/benchmark.png)

*Benchmarks run on: macOS M4 32GB, 100 groups, 20 runs (median), 5 warmup runs. [H2OAI](https://h2oai.github.io/db-benchmark/)*


## Quick Start

```python
>>> from datetime import time
>>> from rayforce import Table, Vector, Symbol, Time, F64
>>> from rayforce.types.table import Column

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

>>> result = (
        quotes
        .select(
            max_bid=Column("bid").max(),
            min_bid=Column("bid").min(),
            avg_ask=Column("ask").mean(),
            records_count=Column("time").count(),
            first_time=Column("time").first(),
        )
        .where((Column("bid") >= 110) & (Column("ask") > 100))
        .by("symbol")
        .execute()
    )
>>> print(result)
┌────────┬─────────┬─────────┬─────────┬───────────────┬──────────────┐
│ symbol │ max_bid │ min_bid │ avg_ask │ records_count │ first_time   │
├────────┼─────────┼─────────┼─────────┼───────────────┼──────────────┤
│ GOOG   │ 202.00  │ 200.00  │ 211.00  │ 3             │ 09:00:00.145 │
├────────┴─────────┴─────────┴─────────┴───────────────┴──────────────┤
│ 1 rows (1 shown) 6 columns (6 shown)                                │
└─────────────────────────────────────────────────────────────────────┘
```

## Installation

Package is available on [PyPI](https://pypi.org/project/rayforce-py/):

```bash
pip install rayforce-py
```

This installation also provides a command-line interface to access the native Rayforce runtime:

```clj
~ $ rayforce
Launching Rayforce...
  RayforceDB: 0.1 Dec  6 2025
  Documentation: https://rayforcedb.com/
  Github: https://github.com/RayforceDB/rayforce
↪ (+ 1 2)
3
```

---

**Built with ❤️ for high-performance data processing | <a href="https://py.rayforcedb.com/content/license.html">MIT Licenced</a> | RayforceDB Team**
