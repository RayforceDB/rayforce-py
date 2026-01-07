from __future__ import annotations

from unittest.mock import patch

import pytest

from rayforce import errors
from rayforce.network.tcp.server import TCPServer


@pytest.fixture
def server():
    return TCPServer(port=5000)


@pytest.mark.parametrize("port", (0, 65536, -1))
def test_init_invalid_port(port):
    with pytest.raises(errors.RayforceTCPError, match="Invalid port"):
        TCPServer(port=port)


@patch("rayforce.network.tcp.server.FFI.ipc_listen")
@patch("rayforce.network.tcp.server.FFI.runtime_run")
def test_listen_success(mock_runtime_run, mock_ipc_listen, server):
    mock_ipc_listen.return_value = 123
    mock_runtime_run.return_value = 0

    server.listen()

    mock_ipc_listen.assert_called_once_with(5000)
    assert server._listener_id == 123
    mock_runtime_run.assert_called_once()


@patch("rayforce.network.tcp.server.FFI.ipc_listen")
@patch("rayforce.network.tcp.server.FFI.runtime_run")
@patch("rayforce.network.tcp.server.FFI.ipc_close_listener")
def test_listen_closes_on_exception(mock_close, mock_runtime_run, mock_ipc_listen, server):
    mock_ipc_listen.return_value = 123
    mock_runtime_run.side_effect = RuntimeError("Test error")

    with pytest.raises(RuntimeError, match="Test error"):
        server.listen()

    mock_ipc_listen.assert_called_once_with(5000)
    mock_close.assert_called_once_with(123)
    assert server._listener_id is None


@patch("rayforce.network.tcp.server.FFI.ipc_listen")
@patch("rayforce.network.tcp.server.FFI.runtime_run")
@patch("rayforce.network.tcp.server.FFI.ipc_close_listener")
def test_listen_closes_on_keyboard_interrupt(mock_close, mock_runtime_run, mock_ipc_listen, server):
    mock_ipc_listen.return_value = 123
    mock_runtime_run.side_effect = KeyboardInterrupt()

    with pytest.raises(KeyboardInterrupt):
        server.listen()

    mock_ipc_listen.assert_called_once_with(5000)
    mock_close.assert_called_once_with(123)
    assert server._listener_id is None
