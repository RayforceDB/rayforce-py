# :material-newspaper: Changelog

All notable changes to Rayforce-Py will be documented in this file.

!!! note ""
    You can also subscribe for release notifications by joining our [:simple-zulip: Zulip](https://rayforcedb.zulipchat.com/#narrow/channel/549008-Discuss)!

## **`0.4.1`**

### New Features

- **Apache Parquet Support (Beta)**: Added `load_parquet()` function to read Parquet files directly into Rayforce Tables. Uses PyArrow for efficient zero-copy data access where possible. See [Parquet documentation](./documentation/plugins/parquet.md) for details.

## Bug fixes
- Fix for temporal type comparisons with integers

2026-01-13 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.4.1/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.4.1)**


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

- [Added `slice()` method to Table for extracting subsets of rows](https://py.rayforcedb.com/content/documentation/data-types/table/access-values.html#slice-a-table)

2025-12-24 | **[🔗 PyPI](https://pypi.org/project/rayforce-py/0.1.5/)** | **[🔗 GitHub](https://github.com/RayforceDB/rayforce-py/releases/tag/0.1.5)**
