# :material-web: WebSocket

Rayforce-Py can expose its runtime over WebSocket connections, letting WebSocket-compatible clients evaluate Rayforce queries using the standard WebSocket protocol.

## :material-information: Overview

The WebSocket layer consists of:

- **`WSServer`** - An async WebSocket server that accepts connections and evaluates Rayforce queries in-process
- **`WSClient`** - A WebSocket client for connecting to a Rayforce WebSocket server
- **`WSClientConnection`** - An individual client connection (returned by `WSClient.connect()`)
- **`WSServerConnection`** - An individual server-side connection (used internally)

Messages use Rayforce's binary IPC serialization (the same format as TCP IPC), framed as WebSocket binary messages. Unlike the [TCP server](./IPC.md), which delegates the wire protocol to Rayforce's native engine, the WebSocket server is an async Python implementation built on the [`websockets`](https://pypi.org/project/websockets/) library — WebSocket framing is not provided by the native IPC layer.

!!! note "Optional Dependency"
    WebSocket support requires the `websockets` library. Install it with the `websocket` extra:
    ```bash
    pip install rayforce-py[websocket]
    ```

---

## :material-server: WebSocket Server

The `WSServer` class creates an async WebSocket server that listens for connections and evaluates incoming queries.

### Creating a Server

Import `WSServer` from the WebSocket module:

```python
>>> from rayforce.network.websocket import WSServer

>>> server = WSServer(port=8765)
>>> server
WSServer(port=8765)
```

### Running the Server

`run()` starts the server and blocks until interrupted (`SIGINT`/`SIGTERM`), cleaning up on exit:

```python
>>> import asyncio
>>> from rayforce.network.websocket import WSServer

>>> async def main():
...     await WSServer(port=8765).run()

>>> asyncio.run(main())
Rayforce WebSocket served on ws://0.0.0.0:8765
^C
Rayforce WebSocket Server stopped.
```

For finer control, `start()` binds the server without blocking and `stop()` shuts it down — useful when embedding the server in an existing event loop:

```python
>>> server = WSServer(port=8765)
>>> await server.start()
>>> # ... server is now accepting connections ...
>>> await server.stop()
```

---

## :material-network: WebSocket Client

The `WSClient` class connects to a Rayforce WebSocket server. Each connection represents a single session.

### Creating a Client

```python
>>> from rayforce.network.websocket import WSClient

>>> client = WSClient(host="localhost", port=8765)
>>> client
WSClient(ws://localhost:8765)
```

### Connecting

`connect()` opens the connection and performs the version handshake:

```python
>>> import asyncio
>>> from rayforce.network.websocket import WSClient

>>> async def main():
...     connection = await WSClient(host="localhost", port=8765).connect()
...     # ... use the connection ...
...     await connection.close()

>>> asyncio.run(main())
```

### Executing Queries

`execute()` sends a query and returns the evaluated result.

#### String Queries

```python
>>> from rayforce import String

>>> result = await connection.execute(String("(+ 1 2)"))
>>> print(result)
3
```

A bare `str` is also accepted and wrapped automatically:

```python
>>> await connection.execute("(sum (til 10))")
45
```

#### Query Objects

WebSocket supports the same query objects as TCP IPC — they are evaluated against a table that lives on the server:

```python
>>> from rayforce import Table, Column

>>> query = Table("server_side_table").select("id", "name").where(Column("id") > 1)
>>> result = await connection.execute(query)
```

Read queries (`select`, joins) return a `Table`. Mutating queries (`update`, `insert`, `upsert`) run against the named server-side table and return the **table name**; re-query the table to observe the effect:

```python
>>> await connection.execute(Table("trades").update(price=100.0).where(Column("id") == 1))
>>> # then verify
>>> await connection.execute(Table("trades").select("id", "price").where(Column("id") == 1))
```

#### SQL Queries

```python
>>> from rayforce.plugins.sql import SQLQuery

>>> query = SQLQuery(Table("employees"), "SELECT dept, AVG(salary) FROM self GROUP BY dept")
>>> result = await connection.execute(query)
```

See the [SQL documentation](./plugins/sql.md) for more details.

### Connection Management

A connection is an async context manager and closes automatically on exit:

```python
>>> from rayforce import String

>>> async with await WSClient(host="localhost", port=8765).connect() as connection:
...     result = await connection.execute(String("(+ 1 2)"))
...     print(result)
3
```

---

## :material-alert: Error Handling

Connection-level failures (bad handshake, unreachable host, executing on a closed connection) raise `RayforceWSError`:

```python
>>> from rayforce import errors
>>> from rayforce.network.websocket import WSClient

>>> async def main():
...     try:
...         connection = await WSClient(host="localhost", port=9999).connect()
...         await connection.execute("(+ 1 2)")
...     except errors.RayforceWSError as e:
...         print(f"WebSocket Error: {e}")
```

Evaluation errors (e.g. an undefined name or a parse error) are returned to the client as a descriptive message rather than raising, and the connection stays usable for subsequent queries.
