from __future__ import annotations

import pytest

from rayforce import String, errors
from rayforce.network.websocket import WSClient, WSServer
from rayforce.network.websocket.server import WSServerConnection


@pytest.mark.parametrize("port", [0, 65536, -1])
def test_invalid_port(port):
    with pytest.raises(errors.RayforceValueError):
        WSServer(port=port)


def test_repr(free_port):
    assert repr(WSServer(port=free_port)) == f"WSServer(port={free_port})"


@pytest.mark.asyncio
async def test_server_starts_and_stops(free_port):
    server = WSServer(port=free_port)
    await server.start()
    assert server._server is not None
    await server.stop()
    assert server._server is None
    assert len(server._connections) == 0


@pytest.mark.asyncio
async def test_stop_without_start_raises(free_port):
    server = WSServer(port=free_port)
    with pytest.raises(errors.RayforceWSError, match="Server not started"):
        await server.stop()


# ---------------------------------------------------------------------------
# Handshake validation (server side, no connection needed)
# ---------------------------------------------------------------------------


def test_validate_handshake_accepts_valid():
    # version byte + 0x00 terminator
    WSServerConnection._validate_handshake(bytes([1, 0x00]))


def test_validate_handshake_rejects_non_bytes():
    with pytest.raises(errors.RayforceWSError, match="Expected binary handshake"):
        WSServerConnection._validate_handshake("not bytes")


def test_validate_handshake_rejects_too_short():
    with pytest.raises(errors.RayforceWSError, match="Expected 2 bytes handshake"):
        WSServerConnection._validate_handshake(bytes([1]))


def test_validate_handshake_rejects_wrong_terminator():
    with pytest.raises(errors.RayforceWSError, match="Expected"):
        WSServerConnection._validate_handshake(bytes([1, 0x01]))


# ---------------------------------------------------------------------------
# Server resilience: a bad query must not drop the connection
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_bad_query_returns_error_string_without_dropping_connection(ws_server):
    _, port = ws_server
    conn = await WSClient(host="localhost", port=port).connect()

    # An undefined name comes back as a descriptive error message, not a crash.
    result = await conn.execute(String("nonexistent_variable"))
    assert "undefined" in str(result)

    # Connection is still usable afterwards.
    assert await conn.execute(String("(+ 2 3)")) == 5

    await conn.close()
