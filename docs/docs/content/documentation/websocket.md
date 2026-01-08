# :material-web: WebSocket

Rayforce-Py provides WebSocket functionality that allows you to expose Rayforce queries over WebSocket connections. This enables WebSocket-compatible clients to interact with Rayforce using the standard WebSocket protocol.

## :material-information: Overview

The WebSocket implementation in Rayforce-Py consists of:

- **`WSServer`** - An async WebSocket server that accepts connections and executes Rayforce queries
- **`WSClient`** - A WebSocket client for connecting to Rayforce WebSocket servers
- **`WSClientConnection`** - Represents an individual WebSocket client connection
- **`WSServerConnection`** - Represents an individual WebSocket server connection (used internally)

The WebSocket implementation uses Rayforce's native IPC protocol for message serialization, ensuring compatibility with Rayforce's binary format while providing a standard WebSocket interface.

!!! note "Optional Dependency"
    WebSocket functionality requires the `websockets` library. Install it with:
    ```bash
    pip install websockets
    ```

---

## :material-server: WebSocket Server

The `WSServer` class creates an async WebSocket server that listens for incoming connections and processes Rayforce queries.

### Installation

First, ensure you have the `websockets` library installed:

```bash
pip install websockets
```

### Creating a Server

Import `WSServer` from the network module:

```python
>>> from rayforce.network.websocket import WSServer

>>> server = WSServer(port=8765)
>>> server
WSServer(port=8765)
```

### Starting and Stopping the Server

The server uses async methods `start()` and `stop()`:

```python
>>> import asyncio
>>> from rayforce.network.websocket import WSServer

>>> async def main():
        await WSServer(port=8765).run()

>>> asyncio.run(main())
Rayforce WebSocket served on ws://0.0.0.0:8765
^C
Rayforce WebSocket Server stopped.
```

---

## :material-network: WebSocket Client

The `WSClient` class allows you to connect to a Rayforce WebSocket server.

### Creating a Client

Import `WSClient` from the network module:

```python
>>> from rayforce.network.websocket import WSClient

>>> client = WSClient(host="localhost", port=8765)
>>> client
WSClient(ws://localhost:8765)
```

### Connecting

Use the `connect()` method to establish a connection:

```python
>>> import asyncio
>>> from rayforce.network.websocket import WSClient

>>> async def main():
        client = WSClient(host="localhost", port=8765)
        connection = await client.connect()
        # Use connection
        await connection.close()

>>> asyncio.run(main())
```

### Executing Queries

The connection's `.execute()` method allows you to send queries to the server:

```python
>>> import asyncio
>>> from rayforce import String
>>> from rayforce.network.websocket import WSClient

>>> async def main():
        client = WSClient(host="localhost", port=8765)
        connection = await client.connect()

        # Execute string queries
        result1 = await connection.execute(String("(+ 1 2)"))
        print(result1)  # 3

        # Execute query objects
        from rayforce import Table, Column
        table = Table("server_table")
        query = table.select("id", "name")
        result2 = await connection.execute(query)

        await connection.close()

>>> asyncio.run(main())
```

### Connection Management

The connection supports async context manager for automatic cleanup:

```python
>>> import asyncio
>>> from rayforce import String
>>> from rayforce.network.websocket import WSClient

>>> async def main():
        client = WSClient(host="localhost", port=8765)
        async with await client.connect() as connection:
            result = await connection.execute("(+ 1 2)")
            print(result)

>>> asyncio.run(main())
I64(3)
```

### Binary Messages

Binary messages must be in Rayforce's native IPC format:

- **Header**: Serialized RayObject using `ser_obj`
- The server deserializes the binary data, evaluates it, and returns the result in the same binary format

---

## :material-alert: Error Handling

WebSocket operations can raise `RayforceWSError` in various scenarios:

```python
>>> from rayforce.network.websocket import WSClient, errors

>>> async def main():
        client = WSClient(host="localhost", port=9999)
        try:
            connection = await client.connect()
            result = await connection.execute(String("(+ 1 2)"))
        except errors.RayforceWSError as e:
            print(f"WebSocket Error: {e}")
```
