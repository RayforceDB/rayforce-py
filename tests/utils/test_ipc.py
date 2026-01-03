from unittest.mock import MagicMock, patch
import pytest

from rayforce import String, _rayforce_c as r
from rayforce.types import Table
from rayforce import errors
from rayforce.utils.ipc import (
    IPCConnection,
    IPCClient,
    IPCServer,
    _python_to_ipc,
)


class TestPythonToIPC:
    def test_python_to_ipc_string(self):
        result = _python_to_ipc("test_string")
        assert String(ptr=result).to_python() == "test_string"

    def test_python_to_ipc_query(self):
        table = Table.from_dict({"col": []})
        query = table.select("col")
        result = _python_to_ipc(query)
        assert isinstance(result, r.RayObject)

    def test_python_to_ipc_unsupported_type(self):
        with pytest.raises(errors.RayforceIPCError, match="Unsupported IPC data"):
            _python_to_ipc(123)


class TestIPCConnection:
    @pytest.fixture
    def mock_engine(self):
        engine = MagicMock(spec=IPCClient)
        engine.pool = {}
        return engine

    @pytest.fixture
    def mock_handle(self):
        handle = MagicMock(spec=r.RayObject)
        return handle

    @pytest.fixture
    def connection(self, mock_engine, mock_handle):
        with patch("rayforce.utils.ipc.FFI.get_obj_type", return_value=r.TYPE_I64):
            return IPCConnection(engine=mock_engine, handle=mock_handle)

    @patch("rayforce.utils.ipc.FFI.write")
    @patch("rayforce.utils.ipc.ray_to_python")
    def test_execute(self, mock_ray_to_python, mock_write, connection):
        mock_write.return_value = MagicMock()
        mock_ray_to_python.return_value = "result"

        result = connection.execute("test_query")
        assert result == "result"
        mock_write.assert_called_once()
        mock_ray_to_python.assert_called_once()

    def test_execute_closed(self, connection):
        connection._closed = True
        with pytest.raises(errors.RayforceIPCError, match="Cannot write to closed connection"):
            connection.execute("test_query")

    @patch("rayforce.utils.ipc.FFI.hclose")
    def test_close_removes_from_pool(self, mock_hclose, mock_engine, mock_handle):
        conn = IPCConnection(engine=mock_engine, handle=mock_handle)
        conn_id = id(conn)
        mock_engine.pool[conn_id] = conn

        conn.close()
        assert conn_id not in mock_engine.pool
        assert conn._closed is True
        mock_hclose.assert_called_once_with(conn.handle)

    @patch("rayforce.utils.ipc.FFI.hclose")
    def test_close_idempotent(self, mock_hclose, connection):
        connection.close()
        connection.close()
        assert mock_hclose.call_count == 1

    def test_context_manager(self, connection):
        with patch.object(connection, "close") as mock_close:
            with connection:
                pass
            mock_close.assert_called_once()


class TestIPCEngine:
    @pytest.fixture
    def engine(self):
        return IPCClient(host="localhost", port=5000)

    @patch("rayforce.utils.ipc.FFI.get_obj_type")
    @patch("rayforce.utils.ipc.FFI.hopen")
    def test_acquire_success(self, mock_hopen, mock_get_obj_type, engine):
        mock_handle = MagicMock(spec=r.RayObject)

        def get_obj_type_side_effect(obj):
            if obj is mock_handle:
                return r.TYPE_I64
            return r.TYPE_C8

        mock_get_obj_type.side_effect = get_obj_type_side_effect
        mock_hopen.return_value = mock_handle

        conn = engine.acquire()
        assert isinstance(conn, IPCConnection)
        assert conn.engine == engine
        assert conn.handle == mock_handle
        assert id(conn) in engine.pool

    @patch("rayforce.utils.ipc.FFI.get_obj_type")
    @patch("rayforce.utils.ipc.FFI.hopen")
    @patch("rayforce.utils.ipc.FFI.get_error_obj")
    def test_acquire_failure(self, mock_get_error, mock_hopen, mock_get_obj_type, engine):
        mock_error = MagicMock(spec=r.RayObject)

        def get_obj_type_side_effect(obj):
            if obj is mock_error:
                return r.TYPE_ERR
            return r.TYPE_C8

        mock_get_obj_type.side_effect = get_obj_type_side_effect
        mock_hopen.return_value = mock_error
        mock_get_error.return_value = "Connection failed"

        with pytest.raises(errors.RayforceIPCError, match="Error when establishing connection"):
            engine.acquire()

    @patch("rayforce.utils.ipc.FFI.get_obj_type")
    @patch("rayforce.utils.ipc.FFI.hopen")
    def test_dispose_connections(self, mock_hopen, mock_get_obj_type, engine):
        mock_handle1 = MagicMock(spec=r.RayObject)
        mock_handle2 = MagicMock(spec=r.RayObject)

        def get_obj_type_side_effect(obj):
            # Return TYPE_C8 for String validation, TYPE_I64 for handles
            if obj is mock_handle1 or obj is mock_handle2:
                return r.TYPE_I64
            # For String objects created during the test, return TYPE_C8
            return r.TYPE_C8

        mock_get_obj_type.side_effect = get_obj_type_side_effect
        mock_hopen.side_effect = [mock_handle1, mock_handle2]

        conn1 = engine.acquire()
        conn2 = engine.acquire()

        with (
            patch.object(conn1, "close") as mock_close1,
            patch.object(conn2, "close") as mock_close2,
        ):
            engine.dispose_connections()
            mock_close1.assert_called_once()
            mock_close2.assert_called_once()

        assert len(engine.pool) == 0


class TestIPCServer:
    @pytest.fixture
    def server(self):
        return IPCServer(port=5000)

    def test_init_valid_port(self):
        server = IPCServer(port=5000)
        assert server.port == 5000
        assert server._listener_id is None

    @pytest.mark.parametrize("port", (0, 65536, -1))
    def test_init_invalid_port_too_low(self, port):
        with pytest.raises(errors.RayforceIPCError, match="Invalid port number"):
            IPCServer(port=port)

    @patch("rayforce.utils.ipc.FFI.ipc_listen")
    @patch("rayforce.utils.ipc.FFI.runtime_run")
    def test_listen_success(self, mock_runtime_run, mock_ipc_listen, server):
        mock_ipc_listen.return_value = 123
        mock_runtime_run.return_value = 0

        server.listen()

        mock_ipc_listen.assert_called_once_with(5000)
        assert server._listener_id == 123
        mock_runtime_run.assert_called_once()

    @patch("rayforce.utils.ipc.FFI.ipc_listen")
    @patch("rayforce.utils.ipc.FFI.runtime_run")
    @patch("rayforce.utils.ipc.FFI.ipc_close_listener")
    def test_listen_closes_on_exception(
        self, mock_close, mock_runtime_run, mock_ipc_listen, server
    ):
        mock_ipc_listen.return_value = 123
        mock_runtime_run.side_effect = RuntimeError("Test error")

        with pytest.raises(RuntimeError, match="Test error"):
            server.listen()

        mock_ipc_listen.assert_called_once_with(5000)
        mock_close.assert_called_once_with(123)
        assert server._listener_id is None

    @patch("rayforce.utils.ipc.FFI.ipc_listen")
    @patch("rayforce.utils.ipc.FFI.runtime_run")
    @patch("rayforce.utils.ipc.FFI.ipc_close_listener")
    def test_listen_closes_on_keyboard_interrupt(
        self, mock_close, mock_runtime_run, mock_ipc_listen, server
    ):
        mock_ipc_listen.return_value = 123
        mock_runtime_run.side_effect = KeyboardInterrupt()

        with pytest.raises(KeyboardInterrupt):
            server.listen()

        mock_ipc_listen.assert_called_once_with(5000)
        mock_close.assert_called_once_with(123)
        assert server._listener_id is None

    def test_repr(self, server):
        repr_str = repr(server)
        assert "IPCServer" in repr_str
        assert "port=5000" in repr_str
