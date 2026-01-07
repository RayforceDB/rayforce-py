from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from rayforce import (
    F64,
    I64,
    Column,
    Symbol,
    Table,
    TableColumnInterval,
    Vector,
)
from rayforce import (
    _rayforce_c as r,
)
from rayforce.ffi import FFI
from rayforce.network.tcp.client import TCPClient
from rayforce.types.scalars import Time
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

    query = Table("t").upsert(match_by_first=1, id="001", age=30)
    result = _capture_and_eval(client, query)

    assert isinstance(result, Symbol)

    result = Table("t").select("*").execute()
    assert result.at_row(0)["id"] == "001"
    assert result.at_row(0)["age"] == 30
