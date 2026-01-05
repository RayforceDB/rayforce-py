# :material-web: WebSocket Server

Rayforce-Py provides WebSocket server functionality that allows you to expose Rayforce queries over WebSocket connections. This enables WebSocket-compatible clients to interact with Rayforce using the standard WebSocket protocol.

## :material-information: Overview

The WebSocket implementation in Rayforce-Py consists of:

- **`WebSocketServer`** - An async WebSocket server that accepts connections and executes Rayforce queries
- **`WebSocketConnection`** - Represents an individual WebSocket connection (used internally)

The WebSocket server uses Rayforce's native IPC protocol for message serialization, ensuring compatibility with Rayforce's binary format while providing a standard WebSocket interface.

!!! note "Optional Dependency"
    WebSocket functionality requires the `websockets` library. Install it with:
    ```bash
    pip install websockets
    ```

---

## :material-server: WebSocket Server

The `WebSocketServer` class creates an async WebSocket server that listens for incoming connections and processes Rayforce queries.

### Installation

First, ensure you have the `websockets` library installed:

```bash
pip install websockets
```

### Creating a Server

Import `WebSocketServer` from the network module:

```python
>>> from rayforce.network.websocket import WebSocketServer

>>> server = WebSocketServer(port=8765)
>>> server
WebSocketServer(port=8765)
```

### Starting the Server

The `run()` method starts the server and runs until stopped (e.g., via Ctrl+C):

```python
>>> import asyncio
>>> from rayforce.network.websocket import WebSocketServer

>>> async def main():
...     server = WebSocketServer(port=8765)
...     await server.run()

>>> asyncio.run(main())
Rayforce WebSocket Server listening on 0.0.0.0:8765
^C
Rayforce WebSocket Server stopped.
```

!!! note "Async Operation"
    The `run()` method is **async** and must be called with `await` or within an async context.

---

## :material-code-tags: Message Format

The WebSocket server accepts two types of messages:

### Text Messages

Text messages are treated as Rayforce string queries and are evaluated directly

### Binary Messages

Binary messages must be in Rayforce's native IPC format:
- **Header**: 16 bytes (prefix, version, flags, endian, msgtype, size)
- **Payload**: Serialized RayObject using `ser_obj`

The server deserializes the binary data, evaluates it, and returns the result in the same binary format.


#### Next: [IPC Documentation](./IPC.md)
