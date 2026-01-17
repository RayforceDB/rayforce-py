# :material-network: IPC Inter-Process Communication

Rayforce-Py provides TCP-based IPC (Inter-Process Communication) functionality to communicate with other Rayforce instances over the network. This allows you to build distributed systems, microservices, and client-server architectures using Rayforce's high-performance runtime.

## :material-information: Overview

TCP IPC in Rayforce-Py consists of two main components:

- **`TCPServer`** - Listens for incoming TCP connections on a specified port
- **`TCPClient`** - Connects to remote Rayforce instances and executes queries

The TCP IPC implementation uses Rayforce's native runtime event loop, ensuring optimal performance and seamless integration with the Rayforce ecosystem.

---

## :material-server: TCP Server

The `TCPServer` class allows you to create a server that listens for incoming TCP connections. The server runs on Rayforce's native event loop.

### Creating a Server

To create a TCP server, import `TCPServer` and initialize it with a port:

```python
>>> from rayforce import TCPServer

>>> server = TCPServer(port=5000)
>>> server
TCPServer(port=5000)
```

### Starting the Server

The `listen()` method starts the server and blocks until the event loop exits:

```python
>>> server.listen()
Rayforce IPC Server listening on 5000 (id:123)
```

!!! note "Blocking Operation"
    The `listen()` method is **blocking** - it will run until the event loop is stopped (e.g., via KeyboardInterrupt or program termination). The server automatically closes the port when the event loop exits, so no manual cleanup is needed.

---

## :material-network: TCP Client

The `TCPClient` class provides a connection to a remote Rayforce instance. Each client represents a single connection.

### Initializing a Client

To use TCP IPC, import `TCPClient`:

```python
>>> from rayforce import TCPClient
```

Then initialize the client for a specific host and port:

```python
>>> client = TCPClient(host="localhost", port=5000)
>>> client
TCPClient(localhost:5000) - alive: True
```

### Executing Queries

The `.execute()` method allows you to send various types of data to the remote Rayforce instance.

#### Sending String Queries

You can send raw string queries:

```python
>>> result = client.execute("(+ 1 2)")
>>> print(result)
3
```

#### Sending Query Objects

TCP IPC supports sending Rayforce query objects directly, providing type safety and better integration:

```python
>>> from rayforce import Table, Column

>>> table = Table("server_side_table_name")
>>> query = table.select("id", "name").where(Column("id") > 1)

>>> result = client.execute(query)
```

TCP IPC supports all major query types: `SelectQuery`, `UpdateQuery`, `InsertQuery`, `UpsertQuery`, `LeftJoin`, `InnerJoin`, `AsofJoin`, `WindowJoin`

#### Sending SQL Queries

You can send SQL queries to remote tables using the `SQLQuery` class:

```python
>>> from rayforce import TCPClient
>>> from rayforce.plugins.sql import SQLQuery

>>> query = SQLQuery("employees", "SELECT dept, AVG(salary) FROM self GROUP BY dept")
>>> result = client.execute(query)
```

See [SQL documentation](./plugins/sql.md#sql-over-ipc) for more details.

## :material-network: IPC Save

The `ipcsave()` method allows you to save query results or tables to a remote Rayforce instance via IPC connections. This method returns an `Expression` that can be executed on a remote server.

```python
>>> from rayforce import Table, Column

>>> table = Table("server_side_table_name")
>>> query = table.select("id", "name").where(Column("id") > 1)

>>> # Save the query result to a variable on the remote server
>>> TCPClient.execute(query.ipcsave("filtered_results"))
```

!!! note ""
    The `ipcsave()` method returns an `Expression` that must be executed on a remote server via an IPC connection. It does not save locally like the `save()` method.


### Connection Management

The `TCPClient` supports context manager for automatic connection cleanup:

```python
>>> with TCPClient(host="localhost", port=5000) as client:
...     result = client.execute("(+ 1 2)")
...     print(result)
```

You can also manually close the connection:

```python
>>> client = TCPClient(host="localhost", port=5000)
>>> result = client.execute("(+ 1 2)")
>>> client.close()
>>> client
TCPClient(localhost:5000) - alive: False
```

---

## :material-alert: Error Handling

TCP IPC operations can raise `RayforceTCPError` in various scenarios:

```python
>>> from rayforce import TCPClient, errors

>>> try:
...     client = TCPClient(host="localhost", port=9999)
...     result = client.execute("(+ 1 2)")
... except errors.RayforceTCPError as e:
...     print(f"TCP Error: {e}")
```
