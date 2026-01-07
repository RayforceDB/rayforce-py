"""Tests for WebSocket query objects execution."""

from __future__ import annotations

import pytest
import pytest_asyncio

from rayforce import F64, I64, Column, Symbol, Table, TableColumnInterval, Time, Vector
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
async def test_select_query_ws(ws_server):
    _, port = ws_server
    client = WSClient(host="localhost", port=port)
    connection = await client.connect()

    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        }
    )
    table.save("t")

    query = Table("t").select("id", "name").where(Column("age") > 30)
    result = await connection.execute(query)

    assert isinstance(result, Table)
    assert result.at_row(0)["id"] == "002"
    assert result.at_row(0)["name"] == "bob"

    await connection.close()


@pytest.mark.asyncio
async def test_update_query_ws(ws_server):
    _, port = ws_server
    client = WSClient(host="localhost", port=port)
    connection = await client.connect()

    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        }
    )
    table.save("t")

    query = Table("t").update(age=35).where(Column("id") == "001")
    result = await connection.execute(query)

    assert isinstance(result, Table)
    assert result.at_row(0)["id"] == "001"
    assert result.at_row(0)["age"] == 35

    await connection.close()


@pytest.mark.asyncio
async def test_insert_query_ws(ws_server):
    _, port = ws_server
    client = WSClient(host="localhost", port=port)
    connection = await client.connect()

    table = Table(
        {
            "id": Vector(items=["001"], ray_type=Symbol),
            "age": Vector(items=[29], ray_type=I64),
        }
    )
    table.save("t")

    query = Table("t").insert(id=["003"], age=[40])
    result = await connection.execute(query)

    assert isinstance(result, Table)
    assert result.at_row(1)["id"] == "003"
    assert result.at_row(1)["age"] == 40

    await connection.close()


@pytest.mark.asyncio
async def test_upsert_query_ws(ws_server):
    _, port = ws_server
    client = WSClient(host="localhost", port=port)
    connection = await client.connect()

    table = Table(
        {
            "id": Vector(items=["001"], ray_type=Symbol),
            "age": Vector(items=[29], ray_type=I64),
        }
    )
    table.save("t")

    query = Table("t").upsert(match_by_first=1, id="001", age=30)
    result = await connection.execute(query)

    assert isinstance(result, Table)
    assert result.at_row(0)["id"] == "001"
    assert result.at_row(0)["age"] == 30

    await connection.close()
