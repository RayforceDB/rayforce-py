from __future__ import annotations

import asyncio

import pytest

from rayforce import String, errors
from rayforce.network.websocket import WSClient


@pytest.mark.asyncio
async def test_client_connects_and_disconnects(ws_server):
    _, port = ws_server
    connection = await WSClient(host="localhost", port=port).connect()

    assert connection is not None
    assert not connection._closed

    await connection.close()
    assert connection._closed


@pytest.mark.asyncio
async def test_handshake_success(ws_server):
    _, port = ws_server
    connection = await WSClient(host="localhost", port=port).connect()
    assert connection is not None
    await connection.close()


@pytest.mark.asyncio
async def test_execute_arithmetic(ws_server):
    _, port = ws_server
    connection = await WSClient(host="localhost", port=port).connect()

    assert await connection.execute(String("(+ 1 2)")) == 3
    assert await connection.execute(String("(* 3 4)")) == 12
    assert await connection.execute(String("(- 10 3)")) == 7

    await connection.close()


@pytest.mark.asyncio
async def test_execute_set_and_get_variable(ws_server):
    _, port = ws_server
    connection = await WSClient(host="localhost", port=port).connect()

    await connection.execute(String("(set x 42)"))
    # bare str is also accepted (python_to_ipc wraps it in String)
    assert await connection.execute("x") == 42

    await connection.close()


@pytest.mark.asyncio
async def test_multiple_clients(ws_server):
    _, port = ws_server
    conn1 = await WSClient(host="localhost", port=port).connect()
    conn2 = await WSClient(host="localhost", port=port).connect()

    assert await conn1.execute(String("(+ 1 2)")) == 3
    assert await conn2.execute(String("(* 3 4)")) == 12
    assert await conn1.execute(String("(+ 1 2)")) == 3

    await conn1.close()
    await conn2.close()


@pytest.mark.asyncio
async def test_context_manager(ws_server):
    _, port = ws_server
    client = WSClient(host="localhost", port=port)

    async with await client.connect() as connection:
        assert await connection.execute(String("(+ 1 2)")) == 3

    assert connection._closed


@pytest.mark.asyncio
async def test_connection_closed_error(ws_server):
    _, port = ws_server
    connection = await WSClient(host="localhost", port=port).connect()
    await connection.close()

    with pytest.raises(errors.RayforceWSError, match="Cannot execute on closed connection"):
        await connection.execute(String("(+ 1 2)"))


@pytest.mark.asyncio
async def test_server_handles_concurrent_requests(ws_server):
    _, port = ws_server
    clients = [WSClient(host="localhost", port=port) for _ in range(5)]
    connections = [await client.connect() for client in clients]

    tasks = [connections[i].execute(String(f"(+ {i} {i})")) for i in range(5)]
    results = await asyncio.gather(*tasks)
    assert results == [0, 2, 4, 6, 8]

    for conn in connections:
        await conn.close()


@pytest.mark.asyncio
async def test_connect_to_dead_port_raises(free_port):
    # Nothing is listening on free_port.
    with pytest.raises(errors.RayforceWSError, match="Failed to connect"):
        await WSClient(host="localhost", port=free_port).connect()


def test_client_repr():
    assert repr(WSClient(host="localhost", port=8080)) == "WSClient(ws://localhost:8080)"


def test_invalid_port():
    with pytest.raises(errors.RayforceValueError):
        WSClient(host="localhost", port=0)
