from __future__ import annotations

import asyncio

import pytest
import pytest_asyncio

from rayforce import String, errors
from rayforce.network.websocket import WSClient, WSServer


@pytest_asyncio.fixture
async def ws_server(free_port: int):
    server = WSServer(port=free_port)
    await server.start()
    try:
        yield server, free_port
    finally:
        await server.stop()


@pytest.mark.asyncio
async def test_client_connects_and_disconnects(ws_server):
    _, port = ws_server
    client = WSClient(host="localhost", port=port)
    connection = await client.connect()

    assert connection is not None
    assert not connection._closed

    await connection.close()
    assert connection._closed


@pytest.mark.asyncio
async def test_handshake_success(ws_server):
    _, port = ws_server
    client = WSClient(host="localhost", port=port)
    connection = await client.connect()

    assert connection is not None
    await connection.close()


@pytest.mark.asyncio
async def test_execute(ws_server):
    _, port = ws_server
    client = WSClient(host="localhost", port=port)
    connection = await client.connect()

    result1 = await connection.execute(String("(+ 1 2)"))
    assert result1 == 3

    result2 = await connection.execute(String("(* 3 4)"))
    assert result2 == 12

    result3 = await connection.execute(String("(- 10 3)"))
    assert result3 == 7

    await connection.execute(String("(set x 42)"))
    result = await connection.execute("x")
    assert result == 42

    # with pytest.raises(errors.RayforceError):
    await connection.execute(String("nonexistent_variable"))

    await connection.close()


@pytest.mark.asyncio
async def test_multiple_clients(ws_server):
    _, port = ws_server
    client1 = WSClient(host="localhost", port=port)
    client2 = WSClient(host="localhost", port=port)

    conn1 = await client1.connect()
    result1 = await conn1.execute(String("(+ 1 2)"))
    assert result1 == 3

    conn2 = await client2.connect()
    result2 = await conn2.execute(String("(* 3 4)"))
    assert result2 == 12

    result1 = await conn1.execute(String("(+ 1 2)"))
    assert result1 == 3

    await conn1.close()
    await conn2.close()


@pytest.mark.asyncio
async def test_context_manager(ws_server):
    _, port = ws_server
    client = WSClient(host="localhost", port=port)

    async with await client.connect() as connection:
        result = await connection.execute(String("(+ 1 2)"))
        assert result == 3

    assert connection._closed


@pytest.mark.asyncio
async def test_connection_closed_error(ws_server):
    _, port = ws_server
    client = WSClient(host="localhost", port=port)
    connection = await client.connect()
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
