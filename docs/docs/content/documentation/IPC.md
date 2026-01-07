# :material-network: IPC Inter-Process Communication

Rayforce-Py provides IPC (Inter-Process Communication) functionality to communicate with other Rayforce instances over the network. This allows you to build distributed systems, microservices, and client-server architectures using Rayforce's high-performance runtime.

## :material-information: Overview

IPC in Rayforce-Py consists of two main components:

- **`IPCServer`** - Listens for incoming connections on a specified port
- **`IPCClient`** - Connects to remote Rayforce instances and executes queries

The IPC implementation uses Rayforce's native runtime event loop, ensuring optimal performance and seamless integration with the Rayforce ecosystem.

---

## :material-server: IPC Server

The `IPCServer` class allows you to create a server that listens for incoming IPC connections. The server runs on Rayforce's native event loop.

### Creating a Server

To create an IPC server, import `IPCServer` and initialize it with a port:

```python
>>> from rayforce import IPCServer

>>> server = IPCServer(port=5000)
>>> server
IPCServer(port=5000)
```

### Starting the Server

The `listen()` method starts the server and blocks until the event loop exits:

```python
>>> server.listen()
Rayforce IPC Server listening on 0.0.0.0:5000 (id:123)
```

!!! note "Blocking Operation"
    The `listen()` method is **blocking** - it will run until the event loop is stopped (e.g., via KeyboardInterrupt or program termination). The server automatically closes the port when the event loop exits, so no manual cleanup is needed.

---

## :material-network: IPC Client

The `IPCClient` class manages connections to remote Rayforce instances. It maintains a connection pool and provides a simple API for executing queries.

### Initializing a Client

To use IPC, first import the `IPCClient` and `IPCConnection`:

```python
>>> from rayforce import IPCClient
```

Then initialize the client for a specific host and port:

```python
>>> client = IPCClient(host="localhost", port=5000)
>>> client
IPCClient(host=localhost, port=5000, pool_size: 0)
```

### Opening a Connection

There are two ways to open a connection with a Rayforce instance.

#### Manual Connection Management

Manually open a connection via the `.acquire()` method:

```python
>>> conn = client.acquire()
>>> conn
Connection(id:4382902992) - established at 2025-09-15T21:33:39.932434
>>> isinstance(conn, IPCConnection)
True
```

Close the connection when done:

```python
>>> conn.close()
>>> conn
Connection(id:4382902992) - disposed at 2025-09-15T21:34:46.752071
```

#### Context Manager (Recommended)

Use the context manager for automatic connection cleanup:

```python
>>> with client.acquire() as conn:
...     print(conn)
Connection(id:4832080144) - established at 2025-09-15T21:35:39.232321
>>> print(conn)
Connection(id:4832080144) - disposed at 2025-09-15T21:35:39.232500
```

---

## :material-code-tags: Executing Queries

The `.execute()` method allows you to send various types of data to the remote Rayforce instance.

### Sending String Queries

You can send raw string queries:

```python
>>> with client.acquire() as conn:
...     result = conn.execute("(+ 1 2)")
>>> print(result)
I64(3)
```

### Sending Query Objects

IPC supports sending Rayforce query objects directly, providing type safety and better integration:

```python
>>> from rayforce import Table, Column

>>> table = Table("server_side_table_name")
>>> query = table.select("id", "name").where(Column("id") > 1)

>>> with client.acquire() as conn:
...     result = conn.execute(query)
```

### Supported Query Types

IPC supports all major query types:

- `SelectQuery` - SELECT operations
- `UpdateQuery` - UPDATE operations
- `InsertQuery` - INSERT operations
- `UpsertQuery` - UPSERT operations
- `LeftJoin`, `InnerJoin`, `WindowJoin` - JOIN operations

---

## :material-database-cog: Connection Pooling

The `IPCClient` maintains a pool of connections. You can manage multiple connections:

```python
>>> client = IPCClient(host="localhost", port=5000)

>>> conn1 = client.acquire()
>>> conn2 = client.acquire()
>>> client
IPCClient(host=localhost, port=5000, pool_size: 2)
```

To dispose all connections at once:

```python
>>> client.dispose_connections()
>>> client
IPCClient(host=localhost, port=5000, pool_size: 0)
```

---

## :material-alert: Error Handling

IPC operations can raise `RayforceTCPError` in various scenarios:

```python
>>> from rayforce import IPCClient, errors

>>> client = IPCClient(host="localhost", port=9999)
>>> try:
...     with client.acquire() as conn:
...         result = conn.execute("(+ 1 2)")
... except errors.RayforceTCPError as e:
...     print(f"IPC Error: {e}")
```

Common error scenarios:

- **Connection refused** - Server is not running or port is incorrect
- **Port already in use** - Another process is using the specified port
- **Connection closed** - Server closed the connection
- **Invalid port** - Port number is out of valid range (1-65535)
