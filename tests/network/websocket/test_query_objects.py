"""Execute Rayforce query objects (and SQL) over a WebSocket connection.

These exercise the python_to_ipc -> serialize -> eval_obj -> serialize path for
compiled query objects, as opposed to plain query strings.
"""

from __future__ import annotations

import pytest

from rayforce import I64, Column, Symbol, Table, Vector
from rayforce.network.websocket import WSClient
from rayforce.plugins.sql import SQLQuery
from tests.helpers.assertions import assert_contains_columns, assert_row


@pytest.mark.asyncio
async def test_select_query_ws(ws_server, make_table):
    _, port = ws_server
    connection = await WSClient(host="localhost", port=port).connect()

    name, _ = make_table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        }
    )

    query = Table(name).select("id", "name").where(Column("age") > 30)
    result = await connection.execute(query)

    assert_row(result, 0, {"id": "002", "name": "bob"})

    await connection.close()


# Mutating queries (update/insert/upsert) run server-side against the named
# table and return the table name (a Symbol), not a materialized Table. The
# effect is verified with a follow-up select over the same connection.


@pytest.mark.asyncio
async def test_update_query_ws(ws_server, make_table):
    _, port = ws_server
    connection = await WSClient(host="localhost", port=port).connect()

    name, _ = make_table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        }
    )

    result = await connection.execute(Table(name).update(age=35).where(Column("id") == "001"))
    assert str(result) == name

    verify = await connection.execute(Table(name).select("id", "age").where(Column("id") == "001"))
    assert_row(verify, 0, {"id": "001", "age": 35})

    await connection.close()


@pytest.mark.asyncio
async def test_insert_query_ws(ws_server, make_table):
    _, port = ws_server
    connection = await WSClient(host="localhost", port=port).connect()

    name, _ = make_table(
        {
            "id": Vector(items=["001"], ray_type=Symbol),
            "age": Vector(items=[29], ray_type=I64),
        }
    )

    result = await connection.execute(Table(name).insert(id=["003"], age=[40]))
    assert str(result) == name

    verify = await connection.execute(Table(name).select("id", "age"))
    assert_row(verify, 1, {"id": "003", "age": 40})

    await connection.close()


@pytest.mark.asyncio
async def test_upsert_query_ws(ws_server, make_table):
    _, port = ws_server
    connection = await WSClient(host="localhost", port=port).connect()

    name, _ = make_table(
        {
            "id": Vector(items=["001"], ray_type=Symbol),
            "age": Vector(items=[29], ray_type=I64),
        }
    )

    result = await connection.execute(Table(name).upsert(key_columns=1, id="001", age=30))
    assert str(result) == name

    verify = await connection.execute(Table(name).select("id", "age").where(Column("id") == "001"))
    assert_row(verify, 0, {"id": "001", "age": 30})

    await connection.close()


@pytest.mark.asyncio
async def test_inner_join_ws(ws_server, make_table):
    _, port = ws_server
    connection = await WSClient(host="localhost", port=port).connect()

    tname, _ = make_table(
        {
            "sym": Vector(items=["AAPL", "GOOGL"], ray_type=Symbol),
            "price": Vector(items=[100, 200], ray_type=I64),
        }
    )
    qname, _ = make_table(
        {
            "sym": Vector(items=["AAPL", "GOOGL"], ray_type=Symbol),
            "bid": Vector(items=[50, 100], ray_type=I64),
            "ask": Vector(items=[75, 150], ray_type=I64),
        }
    )

    query = Table(tname).inner_join(Table(qname), on="sym")
    result = await connection.execute(query)

    assert_contains_columns(result, ["sym", "price", "bid", "ask"])

    await connection.close()


@pytest.mark.asyncio
async def test_left_join_ws(ws_server, make_table):
    _, port = ws_server
    connection = await WSClient(host="localhost", port=port).connect()

    tname, _ = make_table(
        {
            "sym": Vector(items=["AAPL", "MSFT"], ray_type=Symbol),
            "price": Vector(items=[100, 200], ray_type=I64),
        }
    )
    qname, _ = make_table(
        {
            "sym": Vector(items=["AAPL"], ray_type=Symbol),
            "bid": Vector(items=[50], ray_type=I64),
            "ask": Vector(items=[75], ray_type=I64),
        }
    )

    query = Table(tname).left_join(Table(qname), on="sym")
    result = await connection.execute(query)

    assert_contains_columns(result, ["sym", "price", "bid", "ask"])

    await connection.close()


@pytest.mark.asyncio
async def test_sql_select_query_ws(ws_server, make_table):
    _, port = ws_server
    connection = await WSClient(host="localhost", port=port).connect()

    name, _ = make_table(
        {
            "id": Vector(items=[1, 2, 3], ray_type=I64),
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "age": Vector(items=[25, 30, 35], ray_type=I64),
        }
    )

    query = SQLQuery(Table(name), "SELECT name, age FROM self WHERE age > 25")
    result = await connection.execute(query)

    assert len(result) == 2
    names = [v.value for v in result["name"]]
    assert "bob" in names
    assert "charlie" in names

    await connection.close()
