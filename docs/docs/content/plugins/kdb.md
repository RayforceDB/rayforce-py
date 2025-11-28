# KDB Inter-process communication


### Initializing an engine

Raypy allows you to access KDB databases using a seamless raykx IPC.

The connection with KDB database is being established via a dedicated `KDBEngine` type, which holds all connections to the specific KDB instance.

To open the connection, first import the `KDBEngine` into your runtime:
```python
>>> from rayforce.plugins.raykx import KDBEngine
```

Then initialize the engine for a specific domain and port:
```python
>>> engine = KDBEngine(host="localhost", port=5050)
```

This will create a new KDB engine instance with a `pool_size` tracker which helps you to keep track over the opened connections with the KDB instance:
```python
>>> engine
KDBEngine(pool_size: 0)
```

### Opening the connection

There are 2 ways to open the connection with the KDB instance once the engine is initialized.

1. First way is to manually open a connection via the `.acquire()` method of the engine:
```python
>>> conn = engine.acquire()
>>> conn
KDBConnection(id:4382902992) - established at 2025-09-15T21:33:39.932434
```
Right after that the connection be executed (see below) or disposed:
```python
>>> conn.close()
>>> conn
KDBConnection(id:4382902992) - disposed at 2025-09-15T21:34:46.752071
```

2. Second way is to use the context manager, which handles the disposal for you, leaving no open connection outside of the actual manager:
```python
>>> with engine.acquire() as conn:
...    print(conn)
KDBConnection(id:4832080144) - established at 2025-09-15T21:35:39.232321
>>> print(conn)
KDBConnection(id:4832080144) - disposed at 2025-09-15T21:35:39.232500
```

### Executing a query

In order to execute a KDB query, the `.execute()` method has to be called with the actual query being passed as an argument:

```python
>>> with engine.acquire() as conn:
...    conn.execute("x: 150")
...    conn.execute("y: 150")
...    result = conn.execute("x + y")
>>> print(result)
I64(300)
```

Raypy supports executing a query over any type, even with the tables. See local usage example:
```python
>>> engine = KDBEngine(host="localhost", port=6062)

>>> with engine.acquire() as conn:
...    result = conn.execute("0!select sum ExecQty, NotionalValue: sum ExecQty*ExecPrice by Broker, Account from MyTable where date=2025.08.01, Broker in `Bro1`Bro2`Bro3`Bro4")

>>> result
Table[Vector[6](Symbol(Broker), Symbol(Account), Symbol(ExecQty), Symbol(NotionalValue))]

>>> print(result)
┌────────┬─────────┬──────────────┬───────────────┐
│ Broker │ Account │ ExecQty      │ NotionalValue │
├────────┼─────────┼──────────────┼───────────────┤
│ Bro1   │ 100001  │ 404164.00    │ 754027.92     │
│ Bro2   │ 100002  │ 9000.00      │ 1.022542e+06  │
│ Bro3   │ 100003  │ 2900.00      │ 112745.00     │
│ Bro4   │ 100004  │ 604252.00    │ 961689.55     │
...
```