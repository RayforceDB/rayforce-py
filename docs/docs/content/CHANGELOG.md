# :material-newspaper: Changelog

All notable changes to Rayforce-Py will be documented in this file.

!!! note ""
    You can also subscribe for release notifications by joining our [:simple-zulip: Zulip](https://rayforcedb.zulipchat.com/#narrow/channel/549008-Discuss)!


## **`2.1.1`**

### New Features

- **Rebuilt against the latest Rayforce C core**, picking up a batch of engine
  fixes and improvements. Highlights: new partitioned-store helpers
  (`.db.parted.fill`, `.db.parted.tables`) and journal `.log.purge`; an
  `.ipc.open` connect timeout plus fixes for `localhost` / lazy-result IPC
  hangs; and a broad reliability sweep (silent-failure hardening, durable
  column-store format versioning, and a worker-heap teardown crash fix).

2026-06-24 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/2.1.1/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/2.1.1)**

## **`2.1.0`**

### New Features

- **Restored WebSocket support.** The `WSClient` / `WSServer` classes and the
  `rayforce.network.websocket` module are back (they were removed in `2.0.0`).
  The server is an async Python implementation, built on the `websockets`
  library, that evaluates Rayforce queries in-process. Install with the
  `websocket` extra (`pip install rayforce-py[websocket]`). See the
  [WebSocket guide](./documentation/websocket.md).
- **Added the PyArrow plugin.** `from_arrow()` converts a `pyarrow.Table` into a
  Rayforce [`Table`](./documentation/data-types/table/overview.md), mirroring the
  [Polars](./documentation/plugins/polars.md) /
  [Pandas](./documentation/plugins/pandas.md) plugins. A column of strings maps to
  `String` by default, or to `Symbol` via the opt-in `strings_as_symbols=True`
  flag. Requires the `parquet` extra (`pip install rayforce-py[parquet]`).

### Bug fixes

- **Fixed mis-scaled Parquet timestamps.**
  [`load_parquet()`](./documentation/plugins/parquet.md) now reads
  microsecond- and millisecond-precision timestamp columns at the correct
  precision; previously non-nanosecond units were mis-scaled. Parquet reading now
  shares the PyArrow plugin's conversion path.

2026-06-19 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/2.1.0/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/2.1.0)**

## **`2.0.2`**

### New Features

- **Added the `ungroup` verb.** `Table.ungroup()` flattens nested `LIST` columns
  into row form — each list cell expands to one row, with atom columns replicated
  per element (the inverse of a `by`-grouping). Also available as a deferred step
  on select queries: `t.select(...).by(...).ungroup().execute()`.

### Bug fixes

- Fixed a bug when the Timestamp type didn't account for TZ offset when using from_csv handler


2026-06-18 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/2.0.2/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/2.0.2)**

## **`2.0.1`**

### Bug Fixes

Fix Type error when attempting to insert/upsert into an empty table.

2026-06-17 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/2.0.1/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/2.0.1)**

## **`2.0.0`**

First release against the **Rayforce v2 C core**. This is a major release with
breaking changes to the type system, the network layer, and the plugin surface.
The `1.0.x` line continues to be maintained against the v1 core.

### Breaking Changes

- **Built against the Rayforce v2 C core.** The bundled engine, build pipeline
  (`make app`), and binary protocol all target v2. Code written against the v1
  core may need updates — see the items below.
- **Removed the `C8` / `Char` type.** v2 has no standalone character type; a
  single character is now a length-1 [`String`](./documentation/data-types/string.md).
  `C8` is no longer importable from `rayforce`.
- **Removed WebSocket support.** The `WSClient` / `WSServer` classes and the
  entire `rayforce.network.websocket` module have been removed. Use
  [TCP IPC](./documentation/IPC.md) (`TCPClient` / `TCPServer`) for networked queries.
- **Renamed the KDB+ plugin.** `rayforce.plugins.raykx` is now
  [`rayforce.plugins.kdb`](./documentation/plugins/kdb.md); import `KDBEngine`
  from the new path.
- **Renumbered scalar type codes** to match the v2 core. Atoms use the negative
  of these values (see the [Data Types overview](./documentation/data-types/overview.md)):

  | Type | v1 code | v2 code |
  |------|---------|---------|
  | `Symbol` | 6 | 12 |
  | `F64` | 10 | 7 |
  | `Date` | 7 | 8 |
  | `Time` | 8 | 9 |
  | `Timestamp` | 9 | 10 |
  | `String` | — | 13 |
  | `F32` | — | 6 |

### New Features

- **Added the `F32`** (32-bit floating-point) type. Arithmetic on `F32` promotes
  to `F64`.
- **Added the `RayforceLimitError`** exception class (core `EC_LIMIT`).

### Notes

- `String` is now a first-class type (no longer modeled as a vector of `C8`).

2026-06-12 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/2.0.0/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/2.0.0)**

## **`1.0.0`**

- Project has came out of beta. Stable release

2026-04-20 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/1.0.0/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/1.0.0)**

## **`0.6.3`**

### Bug Fixes

- **Integer null sentinel handling**: I16, I32, and I64 scalars now correctly recognize null sentinels (`0Nh`, `0Ni`, `0Nj`) and return `None` from `to_python()`. This fixes null comparisons in operations where unmatched rows returned raw sentinel values (e.g., `-9223372036854775808`) instead of `None`.

2026-04-15 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.6.3/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.6.3)**

## **`0.6.2`**

### Bug Fixes

- Now library passes correct contiguous numpy arrays within `from_numpy` function
- F64 vectors can now be used in `median` calculations

2026-03-15 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.6.2/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.6.2)**

## **`0.6.1`**

### New Features

- **Fancy indexing for Tables**: `Table.__getitem__` now supports multiple indexing modes beyond column access:

    - **Expression filter**: `table[Column("age") > 35]` — filter rows by condition. Supports `&` (and) and `|` (or) for combining expressions.
    - **Integer row access**: `table[0]`, `table[-1]` — access a single row by index, returns a Dict.
    - **Slicing**: `table[1:3]`, `table[:5]`, `table[-2:]` — row slicing backed by the C-level `TAKE` operation.
    - **Index list**: `table[[0, 2, 5]]` — select specific rows by position.

- **`Vector.from_numpy()` auto-widening**: Unsupported numpy dtypes are now automatically widened to the nearest supported type: `float32`/`float16` → `F64`, `int8` → `I16`, `uint16` → `I32`, `uint32` → `I64`.

- **`Vector.from_numpy()` bytes and UUID support**: Byte string arrays (`dtype='S'`) are automatically decoded to Symbol vectors. Object arrays of `uuid.UUID` values are detected and converted to GUID vectors.

- **NaT preservation**: `NaT` (Not-a-Time) values in numpy `datetime64` and `timedelta64` arrays now survive round-trips through `Vector.from_numpy()` and `Vector.to_numpy()`.

### Bug Fixes

- **`Table.to_numpy()` with Timestamp columns**: Fixed `DTypePromotionError` when calling `to_numpy()` on tables containing a mix of incompatible column types (e.g., integers, strings, and timestamps). Mixed-type tables now gracefully fall back to `object` dtype.

- **Filtering F64 by distinct** - fixed

- **`Vector.__getitem__` for U8 vectors**: Fixed U8 vector elements being returned as `B8(True/False)` instead of `U8(value)`. Both types are 1-byte, causing the C-level `at_idx` to misinterpret the type.

- **`Vector.from_numpy()` with explicit `ray_type` for temporal arrays**: Fixed `ValueError: cannot include dtype 'M' in a buffer` when passing `ray_type=Timestamp`, `ray_type=Date`, or `ray_type=Time` with datetime64/timedelta64 arrays.

2026-03-03 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.6.1/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.6.1)**


## **`0.6.0`**

### New Features

- **`Vector.from_numpy()` classmethod**: Create vectors from NumPy arrays via bulk memory copy. Supports numeric types (`int16`, `int32`, `int64`, `float64`, `uint8`, `bool`), string arrays, and temporal types (`datetime64` → `Timestamp`/`Date`, `timedelta64` → `Time`). Handles epoch adjustment between NumPy (1970-01-01) and Rayforce (2000-01-01) automatically.

- **`Vector.to_numpy()` method**: Export vector data to a NumPy array via bulk memory copy.

- **`Vector.to_list()` method**: Export vector data to a Python list via bulk memory copy from the underlying C buffer.

- **`Table.from_dict()` classmethod**: Create tables from a dictionary of NumPy arrays, Python lists, or Vectors.

- **`Table.to_dict()` method**: Export table data to a Python dictionary of lists via bulk memory copy.

- **`Table.to_numpy()` method**: Export table data to a 2D NumPy array via bulk memory copy.

- **`select("*", col=value)` fix**: Using `"*"` with computed columns in `select()` now correctly preserves all existing columns

### Dependencies

- NumPy (`>=2.0.0`) is now a required dependency.

2026-02-21 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.6.0/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.6.0)**


## **`0.5.11`**

### New Features

- **`Timestamp.shift_tz()` method**: Shift a `Timestamp` value by a timezone offset. Accepts any `datetime.tzinfo` (including `datetime.timezone` and `zoneinfo.ZoneInfo`).

- **`Column.shift_tz()` for queries**: Shift an entire column of timestamps by a timezone offset within `select()` expressions.

2026-02-19 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.5.11/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.5.11)**


## **`0.5.10`**

### Bug Fixes
- Various bugfixes to the database operations

2026-02-11 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.5.10/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.5.10)**


## **`0.5.9`**

### Bug Fixes

- Fix boolean operator `is_` performed over lists and vectors within table aggregations

2026-02-11 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.5.9/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.5.9)**


## **`0.5.8`**

### Bug Fixes

- Fix type conversion error during upsert operation

2026-02-10 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.5.8/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.5.8)**


## **`0.5.7`**

### Bug Fixes

- Fix boolean operator `is_` performed over lists within table aggregations

2026-02-10 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.5.7/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.5.7)**


## **`0.5.6`**

### Bug Fixes

- Fix sorting for symbol vectors larger than 32 elements

2026-01-29 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.5.6/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.5.6)**


## **`0.5.5`**

### Breaking Changes

- **SQLQuery API changed**: `SQLQuery` now accepts a `Table` object instead of a table name string. Update calls from `SQLQuery("table_name", query)` to `SQLQuery(Table("table_name"), query)`.

### Bug Fixes

- **Division operators fixed**: Fixed `__truediv__` (`/`) and `__floordiv__` (`//`) being incorrectly swapped for scalars and vectors.
- **Sorting MAPCOMMON columns**: Fixed issue when tables containing MAPCOMMON columns were sorted incorrectly.

2026-01-28 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.5.5/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.5.5)**


## **`0.5.4`**

### New Features

- **SQL over IPC**: Send SQL queries to remote Rayforce servers via TCP or WebSocket using the new `SQLQuery` class. [Documentation](https://py.rayforcedb.com/content/documentation/plugins/sql.html)

2026-01-17 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.5.4/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.5.4)**


## **`0.5.3`**

### New Features

- **SQL Query Support**: Query tables using familiar SQL syntax with the new `Table.sql()` method. Supports `SELECT`, `UPDATE`, `INSERT`, and `UPSERT` (via `ON CONFLICT`) statements. Requires optional `sqlglot` dependency. See [SQL documentation](https://py.rayforcedb.com/content/documentation/plugins/sql.html) for details.

- **Vector type inference**: `Vector` now automatically infers the element type from the first item when `ray_type` is not specified.

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

- **Added WebSocket support**: New `WSClient` and `WSServer` classes in the `rayforce.network.websocket` module for WebSocket-based communication.
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
