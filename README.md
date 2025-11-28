# 🐍 RayPy - Python bindings for RayforceDB

**Python interface to RayforceDB** - a very fast columnar vector database written in pure C.

## Features

- **Pythonic API** - Chainable, fluent query syntax that feels pythonic
- **Seamless Integration** - Direct C API access with controlled garbage collection
- **High Performance** - Minimal overhead between Python and RayforceDB runtime
- **Active Development** - Continuously expanding functionality

## 🚀 Quick Start

```python
from rayforce import Table

demo = Table(
    columns=["id", "name", "age", "salary"],
    values=[
        ["001", "002", "003", "004"],
        ["alice", "bob", "charlie", "dana"],
        [29, 34, 41, 38],
        [100000, 120000, 90000, 85000],
    ],
)

result = demo.select("id", "name", "age").where(demo.age >= 35).execute()

print(result)
┌─────┬─────────┬──────────────────────┐
│ id  │ name    │ age                  │
├─────┼─────────┼──────────────────────┤
│ 003 │ charlie │ 41                   │
│ 004 │ dana    │ 38                   │
├─────┴─────────┴──────────────────────┤
│ 2 rows (2 shown) 3 columns (3 shown) │
└──────────────────────────────────────┘
```

## 📦 Installation

```bash
make all
```

This command will:
- Pull the latest RayforceDB version from GitHub
- Patch headers for Python support
- Build the core library and required plugins
- Set up everything you need to get started

## 📚 Documentation

**Full documentation available at:** https://raypy.rayforcedb.com/

---

**Built with ❤️ for high-performance data processing**
