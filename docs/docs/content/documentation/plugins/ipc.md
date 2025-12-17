# :material-network: IPC Inter-Process Communication

Rayforce-Py provides IPC (Inter-Process Communication) functionality to communicate with other Rayforce instances over the network.

## :material-cog-play-outline: Initializing an Engine

The connection with a Rayforce server is established via a dedicated `IPCEngine` type, which manages all connections to a specific Rayforce instance.

To use IPC, first import the `IPCEngine` and `IPCConnection` into your runtime:

```python
>>> from rayforce import IPCEngine
```

Then initialize the engine for a specific host and port:

```python
>>> engine = IPCEngine(host="localhost", port=5000)
```

This will create a new IPC engine instance with a connection pool tracker:

```python
>>> engine
IPCEngine(host=localhost, port=5000, pool_size: 0)
```

## :material-connection: Opening a Connection

There are two ways to open a connection with a Rayforce instance once the engine is initialized.

### Manual Connection Management

First way is to manually open a connection via the `.acquire()` method of the engine:

```python
>>> conn = engine.acquire()
>>> conn
Connection(id:4382902992) - established at 2025-09-15T21:33:39.932434
>>> isinstance(conn, IPCConnection)
True
```

Right after that the connection can be executed (see below) or disposed:

```python
>>> conn.close()
>>> conn
Connection(id:4382902992) - disposed at 2025-09-15T21:34:46.752071
```

### Context Manager

Second way is to use the context manager, which handles the disposal for you automatically:

```python
>>> with engine.acquire() as conn:
...    print(conn)
Connection(id:4832080144) - established at 2025-09-15T21:35:39.232321
>>> print(conn)
Connection(id:4832080144) - disposed at 2025-09-15T21:35:39.232500
```

## :material-code-tags: Executing Queries

The `.execute()` method allows you to send various types of data to the remote Rayforce instance.

### Sending Strings

You can send raw string queries:

```python
>>> with engine.acquire() as conn:
...    result = conn.execute("(+ 1 2")
>>> print(result)
I64(3)
```

### Sending Query Objects

IPC supports sending Rayforce query objects directly, which provides type safety and better integration:

```python
>>> from rayforce import Table, Column
>>>
>>> table = Table.from_name("server_side_table_name")
>>> query = table.select("id", "name").where(Column("id") > 1)
>>>
>>> with engine.acquire() as conn:
...    result = conn.execute(query)
```

## :material-database-cog: Connection Pooling

The `IPCEngine` maintains a pool of connections. You can manage multiple connections:

```python
>>> engine = IPCEngine(host="localhost", port=5000)

>>> conn1 = engine.acquire()
>>> conn2 = engine.acquire()
>>> engine
IPCEngine(host=localhost, port=5000, pool_size: 2)
```

To dispose all connections at once:

```python
>>> engine.dispose_connections()
>>> engine
IPCEngine(host=localhost, port=5000, pool_size: 0)
```
