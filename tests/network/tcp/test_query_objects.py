from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from rayforce import (
    F64,
    I64,
    Column,
    Symbol,
    Table,
    Vector,
)
from rayforce import (
    _rayforce_c as r,
)
from rayforce.ffi import FFI
from rayforce.network.tcp.client import TCPClient
from rayforce.plugins.sql import SQLQuery
from rayforce.utils import eval_obj


@pytest.fixture
def mock_handle():
    return MagicMock(spec=r.RayObject)


@pytest.fixture
def client(mock_handle):
    def get_obj_type_side_effect(obj):
        if obj == mock_handle:
            return r.TYPE_I64
        return r.TYPE_C8

    with (
        patch("rayforce.network.tcp.client.FFI.get_obj_type", side_effect=get_obj_type_side_effect),
        patch("rayforce.network.tcp.client.FFI.hopen", return_value=mock_handle),
    ):
        return TCPClient(host="localhost", port=5000)


def _capture_and_eval(client, query_obj):
    captured_obj = None

    def capture_write(_handle, data):
        nonlocal captured_obj
        captured_obj = data
        return MagicMock(spec=r.RayObject)

    with (
        patch("rayforce.network.tcp.client.FFI.write", side_effect=capture_write),
        patch("rayforce.network.tcp.client.ray_to_python", return_value="mocked_result"),
    ):
        client.execute(query_obj)

    assert captured_obj is not None
    assert isinstance(captured_obj, r.RayObject)

    obj_type = FFI.get_obj_type(captured_obj)
    assert obj_type != r.TYPE_ERR, "Captured object should not be an error"

    return eval_obj(captured_obj)


def test_select_query_tcp(client):
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        }
    )
    table.save("t")

    query = Table("t").select("id", "name").where(Column("age") > 30)
    result = _capture_and_eval(client, query)

    assert isinstance(result, Table)
    assert result.at_row(0)["id"] == "002"
    assert result.at_row(0)["name"] == "bob"


def test_update_query_tcp(client):
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        }
    )
    table.save("t")

    query = Table("t").update(age=35).where(Column("id") == "001")
    result = _capture_and_eval(client, query)

    assert isinstance(result, Symbol)

    result = Table("t").select("*").execute()
    assert result.at_row(0)["id"] == "001"
    assert result.at_row(0)["age"] == 35


def test_insert_query_tcp(client):
    table = Table(
        {
            "id": Vector(items=["001"], ray_type=Symbol),
            "age": Vector(items=[29], ray_type=I64),
        }
    )
    table.save("t")

    query = Table("t").insert(id=["003"], age=[40])
    result = _capture_and_eval(client, query)

    assert isinstance(result, Symbol)

    result = Table("t").select("*").execute()
    assert result.at_row(1)["id"] == "003"
    assert result.at_row(1)["age"] == 40


def test_upsert_query_tcp(client):
    table = Table(
        {
            "id": Vector(items=["001"], ray_type=Symbol),
            "age": Vector(items=[29], ray_type=I64),
        }
    )
    table.save("t")

    query = Table("t").upsert(key_columns=1, id="001", age=30)
    result = _capture_and_eval(client, query)

    assert isinstance(result, Symbol)

    result = Table("t").select("*").execute()
    assert result.at_row(0)["id"] == "001"
    assert result.at_row(0)["age"] == 30


def test_sql_select_query_tcp(client):
    table = Table(
        {
            "id": Vector(items=[1, 2, 3], ray_type=I64),
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "age": Vector(items=[25, 30, 35], ray_type=I64),
        }
    )
    table.save("employees")

    query = SQLQuery(Table("employees"), "SELECT name, age FROM self WHERE age > 25")
    result = _capture_and_eval(client, query)

    assert isinstance(result, Table)
    assert len(result) == 2


def test_sql_update_query_tcp(client):
    table = Table(
        {
            "id": Vector(items=[1, 2], ray_type=I64),
            "salary": Vector(items=[50000.0, 60000.0], ray_type=F64),
        }
    )
    table.save("employees")

    query = SQLQuery(Table("employees"), "UPDATE self SET salary = 75000.0 WHERE id = 1")
    result = _capture_and_eval(client, query)

    assert isinstance(result, Symbol)

    result = Table("employees").select("*").execute()
    assert result.at_row(0)["salary"] == 75000.0


def test_sql_insert_query_tcp(client):
    table = Table(
        {
            "id": Vector(items=[1], ray_type=I64),
            "name": Vector(items=["alice"], ray_type=Symbol),
        }
    )
    table.save("employees")

    query = SQLQuery(Table("employees"), "INSERT INTO self (id, name) VALUES (2, 'bob')")
    result = _capture_and_eval(client, query)

    assert isinstance(result, Symbol)

    result = Table("employees").select("*").execute()
    assert len(result) == 2
    assert result.at_row(1)["id"] == 2


def test_sql_upsert_query_tcp(client):
    table = Table(
        {
            "id": Vector(items=[1, 2], ray_type=I64),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        }
    )
    table.save("employees")

    query = SQLQuery(
        Table("employees"),
        "INSERT INTO self (id, name) VALUES (1, 'alice_updated') ON CONFLICT (id) DO UPDATE",
    )
    result = _capture_and_eval(client, query)

    assert isinstance(result, Symbol)

    result = Table("employees").select("*").execute()
    assert result.at_row(0)["name"] == "alice_updated"


def test_sql_complex_select_tcp(client):
    table = Table(
        {
            "dept": Vector(items=["eng", "sales", "eng", "sales"], ray_type=Symbol),
            "salary": Vector(items=[100000.0, 60000.0, 120000.0, 70000.0], ray_type=F64),
        }
    )
    table.save("employees")

    query = SQLQuery(
        Table("employees"),
        "SELECT dept, AVG(salary) AS avg_salary FROM self GROUP BY dept",
    )
    result = _capture_and_eval(client, query)

    assert isinstance(result, Table)
    assert len(result) == 2
    assert "dept" in result.columns()
    assert "avg_salary" in result.columns()
