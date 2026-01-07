from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from rayforce import String, errors
from rayforce import _rayforce_c as r
from rayforce.network.tcp.client import TCPClient


@pytest.fixture
def mock_handle():
    handle = MagicMock(spec=r.RayObject)
    return handle


@patch("rayforce.network.tcp.client.FFI.get_obj_type")
@patch("rayforce.network.tcp.client.FFI.hopen")
def test_execute_success(mock_hopen, mock_get_obj_type, mock_handle):
    mock_result = MagicMock(spec=r.RayObject)

    def get_obj_type_side_effect(obj):
        if obj == mock_handle:
            return r.TYPE_I64
        return r.TYPE_C8

    mock_get_obj_type.side_effect = get_obj_type_side_effect
    mock_hopen.return_value = mock_handle

    client = TCPClient(host="localhost", port=5000)

    with (
        patch("rayforce.network.tcp.client.FFI.write", return_value=mock_result) as mock_write,
        patch("rayforce.network.tcp.client.ray_to_python", return_value="result") as mock_convert,
    ):
        result = client.execute(String("test_query"))
        assert result == "result"
        mock_write.assert_called_once()
        mock_convert.assert_called_once()


@patch("rayforce.network.tcp.client.FFI.get_obj_type")
@patch("rayforce.network.tcp.client.FFI.hopen")
def test_execute_closed(mock_hopen, mock_get_obj_type, mock_handle):
    def get_obj_type_side_effect(obj):
        if obj == mock_handle:
            return r.TYPE_I64
        return r.TYPE_C8

    mock_get_obj_type.side_effect = get_obj_type_side_effect
    mock_hopen.return_value = mock_handle

    client = TCPClient(host="localhost", port=5000)
    client._alive = False

    with pytest.raises(errors.RayforceTCPError, match="Cannot write to closed connection"):
        client.execute(String("test_query"))


@patch("rayforce.network.tcp.client.FFI.get_obj_type")
@patch("rayforce.network.tcp.client.FFI.hopen")
@patch("rayforce.network.tcp.client.FFI.hclose")
def test_close(mock_hclose, mock_hopen, mock_get_obj_type, mock_handle):
    def get_obj_type_side_effect(obj):
        if obj == mock_handle:
            return r.TYPE_I64
        return r.TYPE_C8

    mock_get_obj_type.side_effect = get_obj_type_side_effect
    mock_hopen.return_value = mock_handle

    client = TCPClient(host="localhost", port=5000)
    client.close()

    assert client._alive is False
    mock_hclose.assert_called_once_with(mock_handle)


@patch("rayforce.network.tcp.client.FFI.get_obj_type")
@patch("rayforce.network.tcp.client.FFI.hopen")
def test_context_manager(mock_hopen, mock_get_obj_type, mock_handle):
    def get_obj_type_side_effect(obj):
        if obj == mock_handle:
            return r.TYPE_I64
        return r.TYPE_C8

    mock_get_obj_type.side_effect = get_obj_type_side_effect
    mock_hopen.return_value = mock_handle

    with patch.object(TCPClient, "close") as mock_close:
        with TCPClient(host="localhost", port=5000) as client:
            assert client is not None
        mock_close.assert_called_once()
