from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from rayforce import String, errors
from rayforce import _rayforce_c as r
from rayforce.network.tcp.client import TCPClient

pytestmark = pytest.mark.network


@pytest.fixture
def mock_handle():
    return MagicMock(spec=r.RayObject)


def _obj_type_for(handle):
    """Return a side_effect callable that maps *handle* to TYPE_I64, else TYPE_C8."""

    def _side_effect(obj):
        return r.TYPE_I64 if obj == handle else r.TYPE_C8

    return _side_effect


def _make_client(mock_handle):
    """Create a TCPClient with mocked hopen and get_obj_type."""
    with (
        patch(
            "rayforce.network.tcp.client.FFI.get_obj_type", side_effect=_obj_type_for(mock_handle)
        ),
        patch("rayforce.network.tcp.client.FFI.hopen", return_value=mock_handle),
    ):
        return TCPClient(host="localhost", port=5000)


def test_execute_success(mock_handle):
    client = _make_client(mock_handle)
    mock_result = MagicMock(spec=r.RayObject)

    with (
        patch("rayforce.network.tcp.client.FFI.write", return_value=mock_result) as mock_write,
        patch("rayforce.network.tcp.client.ray_to_python", return_value="result") as mock_convert,
    ):
        result = client.execute(String("test_query"))
        assert result == "result"
        mock_write.assert_called_once()
        mock_convert.assert_called_once()


def test_execute_closed(mock_handle):
    client = _make_client(mock_handle)
    client._alive = False

    with pytest.raises(errors.RayforceTCPError, match="Cannot write to closed connection"):
        client.execute(String("test_query"))


def test_close(mock_handle):
    with (
        patch(
            "rayforce.network.tcp.client.FFI.get_obj_type", side_effect=_obj_type_for(mock_handle)
        ),
        patch("rayforce.network.tcp.client.FFI.hopen", return_value=mock_handle),
        patch("rayforce.network.tcp.client.FFI.hclose") as mock_hclose,
    ):
        client = TCPClient(host="localhost", port=5000)
        client.close()

        assert client._alive is False
        mock_hclose.assert_called_once_with(mock_handle)


def test_context_manager(mock_handle):
    client = _make_client(mock_handle)

    with patch.object(TCPClient, "close") as mock_close:
        with client:
            assert client is not None
        mock_close.assert_called_once()
