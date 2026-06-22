from __future__ import annotations

import socket

import pytest
import pytest_asyncio

from rayforce.network.websocket import WSServer


@pytest.fixture
def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        return s.getsockname()[1]


@pytest_asyncio.fixture
async def ws_server(free_port: int):
    """In-process WebSocket server (start() is non-blocking, so the server and
    the client share the test's event loop)."""
    server = WSServer(port=free_port)
    await server.start()
    try:
        yield server, free_port
    finally:
        await server.stop()
