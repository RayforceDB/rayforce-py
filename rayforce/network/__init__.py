from .ipc import IPCClient, IPCConnection, IPCServer

__all__ = [
    "IPCClient",
    "IPCConnection",
    "IPCServer",
]

# Import WebSocket classes conditionally
try:
    from .websocket import (  # noqa: F401
        WebSocketClient,
        WebSocketClientConnection,
        WebSocketServer,
    )

    __all__.extend(["WebSocketClient", "WebSocketClientConnection", "WebSocketServer"])
except ImportError:
    pass
