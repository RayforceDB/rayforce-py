# :fontawesome-solid-q: KDB Inter-Process communication


### Initializing an engine

Rayforce-Py allows you to access KDB databases using a seamless IPC client.

The connection with KDB database is being established via a dedicated `KDBEngine` type, which holds all connections to the specific KDB instance.

To open the connection, first import the `KDBEngine` into your runtime:
```python
>>> from rayforce.plugins.kdb import KDBEngine
```

Then initialize the engine for a specific domain and port:
```python
>>> engine = KDBEngine(host="localhost", port=5050)
```

This will create a new KDB engine instance with a `pool_size` tracker which helps you to keep track over the opened connections with the KDB instance:
```python
>>> engine
KDBEngine(localhost:5050, pool_size: 0)
```

### Opening the connection

There are 2 ways to open the connection with the KDB instance once the engine is initialized.

1. First way is to manually open a connection via the `.acquire()` method of the engine:
```python
>>> conn = engine.acquire()
>>> conn
KDBConnection(id:4382902992) - established at 2025-09-15T21:33:39.932434+00:00
```
Right after that the connection be executed (see below) or disposed:
```python
>>> conn.close()
>>> conn
KDBConnection(id:4382902992) - disposed at 2025-09-15T21:34:46.752071+00:00
```

2. Second way is to use the context manager, which handles the disposal for you, leaving no open connection outside of the actual manager:
```python
>>> with engine.acquire() as conn:
...    print(conn)
KDBConnection(id:4832080144) - established at 2025-09-15T21:35:39.232321+00:00
>>> print(conn)
KDBConnection(id:4832080144) - disposed at 2025-09-15T21:35:39.232500+00:00
```

### Executing a query

In order to execute a KDB query, the `.execute()` method has to be called with the actual query being passed as an argument:

```python
>>> with engine.acquire() as conn:
...    result = conn.execute("x: 150; y: 150; x + y")
>>> print(result)
I64(300)
```

Rayforce-Py supports executing a query over any type, including tables:
```python
>>> with engine.acquire() as conn:
...     result = conn.execute(
...         "0!select sum ExecQty by Broker from "
...         "([] Broker:`Bro1`Bro1`Bro2`Bro3; ExecQty:404164 100000 9000 2900)"
...     )

>>> result
Table[Symbol('Broker'), Symbol('ExecQty')]

>>> print(result)
┌────────┬────────────────────────────┐
│ Broker │          ExecQty           │
│  SYM   │            I64             │
├────────┼────────────────────────────┤
│ Bro1   │ 504164                     │
│ Bro2   │ 9000                       │
│ Bro3   │ 2900                       │
├────────┴────────────────────────────┤
│ 3 rows (3 shown) 2 columns (2 shown)│
└─────────────────────────────────────┘
```
