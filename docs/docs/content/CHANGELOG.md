# :material-newspaper: Changelog

All notable changes to Rayforce-Py will be documented in this file.

!!! note ""
    You can also subscribe for release notifications by joining our [:simple-zulip: Zulip](https://rayforcedb.zulipchat.com/#narrow/channel/549008-Discuss)!


## **`0.5.3`**

### New Features

- **SQL Query Support**: Query tables using familiar SQL syntax with the new `Table.sql()` method. Supports `SELECT`, `UPDATE`, `INSERT`, and `UPSERT` (via `ON CONFLICT`) statements. Requires optional `sqlglot` dependency. See [SQL documentation](./documentation/plugins/sql.md) for details.

  ```python
  # SELECT with WHERE, GROUP BY, ORDER BY
  result = table.sql("SELECT dept, AVG(salary) FROM self WHERE age > 25 GROUP BY dept")

  # UPDATE with expressions
  result = table.sql("UPDATE self SET salary = salary * 1.1 WHERE rating > 4")

  # INSERT
  result = table.sql("INSERT INTO self (id, name) VALUES (1, 'Alice'), (2, 'Bob')")

  # UPSERT (insert or update)
  result = table.sql("INSERT INTO self (id, name) VALUES (1, 'Updated') ON CONFLICT (id) DO UPDATE")
  ```

- **Vector type inference**: `Vector` now automatically infers the element type from the first item when `ray_type` is not specified.

  ```python
  # Before: ray_type was required
  v = Vector([1, 2, 3], ray_type=I64)

  # Now: type is inferred automatically
  v = Vector([1, 2, 3])  # Infers I64 from first element
  ```

2026-01-17 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.5.3/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.5.3)**


## **`0.5.2`**

### New Features

- **Vector operations**: Added operations for Vector types including arithmetic (`+`, `-`, `*`, `/`), comparison (`<`, `<=`, `>`, `>=`, `eq`, `ne`), logical (`and_`, `or_`, `not_`), aggregation (`sum`, `min`, `max`, `average`), element access (`first`, `last`, `take`, `at`), set operations (`union`, `sect`, `except_`), search (`find`, `within`, `filter`), sort (`asc`, `desc`, `iasc`, `rank`, `reverse`, `negate`), and functional (`map`).

- **Dict operations**: Added key/value access (`key`, `value`) and sort operations (`asc`, `desc`) for Dict types.

- **Scalar operations**: Added arithmetic, comparison, and math operations (`ceil`, `floor`, `round`) for numeric scalar types (I16, I32, I64, F64).

2026-01-16 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.5.2/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.5.2)**


## **`0.5.1`**

### New Features

- **`pivot()` method**: Reshape data from long to wide format. Supports multiple index columns and aggregation functions (`sum`, `count`, `avg`, `min`, `max`, `first`, `last`). See [Pivot documentation](https://py.rayforcedb.com/content/documentation/query-guide/pivot.md) for details.

2026-01-16 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.5.1/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.5.1)**


## **`0.5.0`**

### Breaking Changes

- **`slice()` renamed to `take()`**: The `slice(start_idx, tail)` method has been renamed to `take(n, offset=0)` with a cleaner signature.

- **`match_by_first` renamed to `key_columns`**: In `upsert()`, the parameter `match_by_first` has been renamed to `key_columns` for clarity.

- **`Table.from_parted`** now accepts `name` instead of `symfile` argument.

- **Sorting API changed**: `xasc()` and `xdesc()` methods have been replaced with `order_by(*cols, desc=False)` which returns a query that must be executed. This allows chaining with other query operations. See [Order By documentation](https://py.rayforcedb.com/content/documentation/query-guide/order-by.md).


### New Features

- **Bracket notation access**: Access columns using `table["col"]` for a single column or `table[["col1", "col2"]]` for multiple columns.

- **`shape()`**: method returns `(rows, cols)` to see table shape

- **`len()` support**: Get row count with `len(table)`.

- **`head()` and `tail()` methods**: Get first/last n rows with `table.head(5)` or `table.tail(5)`.

- **`describe()` method**: Get summary statistics (count, mean, min, max) for numeric columns.

- **`dtypes` property**: Get column types as a dictionary with `table.dtypes`.

- **`drop()` method**: Remove columns with `table.drop("col1", "col2")`. See [Transform documentation](https://py.rayforcedb.com/content/documentation/data-types/table/transform.html).

- **`rename()` method**: Rename columns with `table.rename({"old": "new"})`. See [Transform documentation](https://py.rayforcedb.com/content/documentation/data-types/table/transform.html).

- **`cast()` method**: Change column types with `table.cast("col", I64)`. See [Transform documentation](https://py.rayforcedb.com/content/documentation/data-types/table/transform.html).

- **Chainable `order_by()`**: Sort results as part of query chain: `table.select(...).where(...).order_by("col").execute()`.

### Bug fixes

- Fix issue when applying a boolean vector filter for a table.

2026-01-15 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.5.0/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.5.0)**


## **`0.4.3`**

### New Features

- **Apache Parquet Support (Beta)**: Added `load_parquet()` function to read Parquet files directly into Rayforce Tables. Uses PyArrow for efficient zero-copy data access where possible. See [Parquet documentation](./documentation/plugins/parquet.md) for details.

2026-01-14 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.4.3/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.4.3)**


## **`0.4.2`**

### Bug fixes
- Fix CI/CD Makefile patch for manylinux container CPU flags

2026-01-14 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.4.2/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.4.2)**


## **`0.4.0`**

### Breaking Changes

- **Network module restructuring**: IPC classes (`IPCClient`, `IPCConnection`, `IPCServer`) have been removed from the main package exports and replaced with TCP classes (`TCPClient`, `TCPServer`). The IPC functionality has been reorganized into the `rayforce.network` module.

- **Error class renamed**: `RayforceIPCError` has been removed and replaced with `RayforceTCPError` for network-related errors.

- **Table initialization API changed**: `Table.from_dict()` and `Table.from_name()` methods are removed. Use Table(dict/str) constructor directly instead.


### New Features

- **Added WebSocket support**: New `WSClient` and `WSServer` classes in `rayforce.network.websocket` module for WebSocket-based communication. See [WebSocket documentation](./documentation/websocket.md) for details.
- **Added TCP client/server**: New `TCPClient` and `TCPServer` classes in `rayforce.network.tcp` module exported from the main package.
- **Added `asof_join()` method** to `Table` class for as-of joins (time-based joins). See [Joins documentation](./documentation/query-guide/joins.md#as-of-join) for details.
- **Added `ipcsave()` method** to `Table` and query objects (`SelectQuery`, `UpdateQuery`, `InsertQuery`, `UpsertQuery`, `LeftJoin`, `InnerJoin`, `AsofJoin`, `WindowJoin`) for saving query results in IPC connections.

2026-01-08 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.4.0/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.4.0)**


## **`0.3.1`**

- Improve client-side IPC by allowing sending pythonic queries into the IPC connection
https://py.rayforcedb.com/content/documentation/IPC.html#sending-query-objects

2026-01-04 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.3.1/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.3.1)**


## **`0.3.0`**

- Add server-side IPC - initializing a Rayforce server via Python runtime
- Improve IPC Client-side interface

2026-01-03 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.3.0/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.3.0)**


## **`0.2.2`**

- Better C API error handling
- Performance improvements for initializing RF types from python collections (List, Vector, Table)

2026-01-02 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.2.2/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.2.2)**


## **`0.2.1`**

- C API speedup improvements
- Add thread-safety block to disallow calling runtime from multiple threads

2025-12-28 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.2.1/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.2.1)**


## **`0.2.0`**

- Enhanced error handling
- Core speedup improvements

2025-12-28 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.2.0/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.2.0)**


## **`0.1.5`**

- Added `slice()` method to Table for extracting subsets of rows (renamed to `take()` in 0.4.4)

2025-12-24 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.1.5/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.1.5)**
