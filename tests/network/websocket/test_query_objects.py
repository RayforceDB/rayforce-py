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


@pytest.mark.asyncio
async def test_inner_join_ws(ws_server):
    _, port = ws_server
    client = WSClient(host="localhost", port=port)
    connection = await client.connect()

    trades = Table(
        {
            "sym": Vector(items=["AAPL", "GOOGL"], ray_type=Symbol),
            "price": Vector(items=[100, 200], ray_type=I64),
        }
    )
    trades.save("trades")

    quotes = Table(
        {
            "sym": Vector(items=["AAPL", "GOOGL"], ray_type=Symbol),
            "bid": Vector(items=[50, 100], ray_type=I64),
            "ask": Vector(items=[75, 150], ray_type=I64),
        }
    )
    quotes.save("quotes")

    query = Table("trades").inner_join(Table("quotes"), on="sym")
    result = await connection.execute(query)

    assert isinstance(result, Table)
    columns = result.columns()
    assert "sym" in columns
    assert "price" in columns
    assert "bid" in columns
    assert "ask" in columns

    await connection.close()


@pytest.mark.asyncio
async def test_left_join_ws(ws_server):
    _, port = ws_server
    client = WSClient(host="localhost", port=port)
    connection = await client.connect()

    trades = Table(
        {
            "sym": Vector(items=["AAPL", "MSFT"], ray_type=Symbol),
            "price": Vector(items=[100, 200], ray_type=I64),
        }
    )
    trades.save("trades")

    quotes = Table(
        {
            "sym": Vector(items=["AAPL"], ray_type=Symbol),
            "bid": Vector(items=[50], ray_type=I64),
            "ask": Vector(items=[75], ray_type=I64),
        }
    )
    quotes.save("quotes")

    query = Table("trades").left_join(Table("quotes"), on="sym")
    result = await connection.execute(query)

    assert isinstance(result, Table)
    columns = result.columns()
    assert "sym" in columns
    assert "price" in columns
    assert "bid" in columns
    assert "ask" in columns

    await connection.close()


@pytest.mark.asyncio
async def test_asof_join_ws(ws_server):
    _, port = ws_server
    client = WSClient(host="localhost", port=port)
    connection = await client.connect()

    trades = Table(
        {
            "sym": Vector(items=["AAPL", "AAPL"], ray_type=Symbol),
            "ts": Vector(
                items=[Time("09:00:00.100"), Time("09:00:00.200")],
                ray_type=Time,
            ),
            "price": Vector(items=[100, 200], ray_type=I64),
        }
    )
    trades.save("trades")

    quotes = Table(
        {
            "sym": Vector(items=["AAPL", "AAPL"], ray_type=Symbol),
            "ts": Vector(
                items=[Time("09:00:00.050"), Time("09:00:00.150")],
                ray_type=Time,
            ),
            "bid": Vector(items=[45, 55], ray_type=I64),
            "ask": Vector(items=[70, 80], ray_type=I64),
        }
    )
    quotes.save("quotes")

    query = Table("trades").asof_join(Table("quotes"), on=["sym", "ts"])
    result = await connection.execute(query)

    assert isinstance(result, Table)
    columns = result.columns()
    assert "sym" in columns
    assert "ts" in columns
    assert "price" in columns
    assert "bid" in columns
    assert "ask" in columns

    await connection.close()


@pytest.mark.asyncio
async def test_window_join_ws(ws_server):
    _, port = ws_server
    client = WSClient(host="localhost", port=port)
    connection = await client.connect()

    trades = Table(
        {
            "sym": Vector(items=["AAPL"], ray_type=Symbol),
            "tt": Vector(items=[Time("09:00:00.100")], ray_type=Time),
            "price": Vector(items=[150.0], ray_type=F64),
        }
    )
    trades.save("trades")

    quotes = Table(
        {
            "sym": Vector(items=["AAPL", "AAPL"], ray_type=Symbol),
            "tt": Vector(
                items=[Time("09:00:00.095"), Time("09:00:00.105")],
                ray_type=Time,
            ),
            "bid": Vector(items=[99.0, 101.0], ray_type=F64),
            "ask": Vector(items=[109.0, 111.0], ray_type=F64),
        }
    )
    quotes.save("quotes")

    interval = TableColumnInterval(
        lower=-10,
        upper=10,
        table=Table("trades"),
        column=Column("tt"),
    )

    query = Table("trades").window_join(
        on=["sym", "tt"],
        interval=interval,
        join_with=[Table("quotes")],
        min_bid=Column("bid").min(),
        max_ask=Column("ask").max(),
    )
    result = await connection.execute(query)

    assert isinstance(result, Table)
    columns = result.columns()
    assert "min_bid" in columns
    assert "max_ask" in columns

    await connection.close()


@pytest.mark.asyncio
async def test_window_join1_ws(ws_server):
    _, port = ws_server
    client = WSClient(host="localhost", port=port)
    connection = await client.connect()

    trades = Table(
        {
            "sym": Vector(items=["AAPL"], ray_type=Symbol),
            "tt": Vector(items=[Time("09:00:00.100")], ray_type=Time),
            "price": Vector(items=[150.0], ray_type=F64),
        }
    )
    trades.save("trades")

    quotes = Table(
        {
            "sym": Vector(items=["AAPL", "AAPL"], ray_type=Symbol),
            "tt": Vector(
                items=[Time("09:00:00.095"), Time("09:00:00.105")],
                ray_type=Time,
            ),
            "bid": Vector(items=[99.0, 101.0], ray_type=F64),
            "ask": Vector(items=[109.0, 111.0], ray_type=F64),
        }
    )
    quotes.save("quotes")

    interval = TableColumnInterval(
        lower=-10,
        upper=10,
        table=Table("trades"),
        column=Column("tt"),
    )

    query = Table("trades").window_join1(
        on=["sym", "tt"],
        interval=interval,
        join_with=[Table("quotes")],
        min_bid=Column("bid").min(),
        max_ask=Column("ask").max(),
    )
    result = await connection.execute(query)

    assert isinstance(result, Table)
    columns = result.columns()
    assert "min_bid" in columns
    assert "max_ask" in columns

    await connection.close()
