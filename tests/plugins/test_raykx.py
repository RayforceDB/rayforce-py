from unittest.mock import MagicMock, patch
import pytest

from rayforce import _rayforce_c as r
from rayforce.plugins.raykx import KDBConnection, KDBEngine
from rayforce.plugins import errors


class TestKDBConnection:
    @pytest.fixture
    def mock_engine(self):
        engine = MagicMock(spec=KDBEngine)
        engine.pool = {}
        return engine

    @pytest.fixture
    def mock_conn(self):
        conn = MagicMock(spec=r.RayObject)
        conn.get_obj_type.return_value = -r.TYPE_I64
        return conn

    @pytest.fixture
    def connection(self, mock_engine, mock_conn):
        return KDBConnection(engine=mock_engine, conn=mock_conn)

    def test_init_invalid_type(self, mock_engine):
        invalid_conn = MagicMock(spec=r.RayObject)
        invalid_conn.get_obj_type.return_value = r.TYPE_ERR

        with pytest.raises(errors.KDBConnectionError, match="Invalid KDB connection object type"):
            KDBConnection(engine=mock_engine, conn=invalid_conn)

    @patch("rayforce.plugins.raykx.FFI.eval_obj")
    @patch("rayforce.plugins.raykx.FFI.init_string")
    @patch("rayforce.plugins.raykx.FFI.push_obj")
    @patch("rayforce.plugins.raykx.FFI.init_list")
    @patch("rayforce.plugins.raykx.utils.ray_to_python")
    def test_execute(
        self,
        mock_ray_to_python,
        mock_init_list,
        mock_push_obj,
        mock_init_string,
        mock_eval_obj,
        connection,
    ):
        mock_result = MagicMock(spec=r.RayObject)
        mock_result.get_obj_type.return_value = r.TYPE_I64
        mock_eval_obj.return_value = mock_result
        mock_ray_to_python.return_value = "result"

        result = connection.execute("test_query")
        assert result == "result"
        mock_eval_obj.assert_called_once()
        mock_ray_to_python.assert_called_once()

    def test_execute_closed(self, connection):
        connection.is_closed = True
        with pytest.raises(errors.KDBConnectionAlreadyClosedError):
            connection.execute("test_query")

    @patch("rayforce.plugins.raykx.FFI.eval_obj")
    @patch("rayforce.plugins.raykx.FFI.get_error_obj")
    @patch("rayforce.plugins.raykx.FFI.init_string")
    @patch("rayforce.plugins.raykx.FFI.push_obj")
    @patch("rayforce.plugins.raykx.FFI.init_list")
    def test_execute_error_ipc_send(
        self,
        mock_init_list,
        mock_push_obj,
        mock_init_string,
        mock_get_error,
        mock_eval_obj,
        connection,
    ):
        mock_error = MagicMock(spec=r.RayObject)
        mock_error.get_obj_type.return_value = r.TYPE_ERR
        mock_eval_obj.return_value = mock_error
        mock_get_error.return_value = "'ipc_send error"

        with pytest.raises(errors.KDBConnectionAlreadyClosedError):
            connection.execute("test_query")

    @pytest.mark.xfail  # temp: resolve issue with IPC errors in rayforce
    @patch("rayforce.plugins.raykx.FFI.eval_obj")
    @patch("rayforce.plugins.raykx.FFI.get_error_obj")
    @patch("rayforce.plugins.raykx.FFI.init_string")
    @patch("rayforce.plugins.raykx.FFI.push_obj")
    @patch("rayforce.plugins.raykx.FFI.init_list")
    def test_execute_error_other(
        self,
        mock_init_list,
        mock_push_obj,
        mock_init_string,
        mock_get_error,
        mock_eval_obj,
        connection,
    ):
        mock_error = MagicMock(spec=r.RayObject)
        mock_error.get_obj_type.return_value = r.TYPE_ERR
        mock_eval_obj.return_value = mock_error
        mock_get_error.return_value = "Other error"

        with pytest.raises(ValueError, match="Failed to execute statement"):
            connection.execute("test_query")

    @patch("rayforce.plugins.raykx.FFI.eval_obj")
    @patch("rayforce.plugins.raykx.FFI.push_obj")
    @patch("rayforce.plugins.raykx.FFI.init_list")
    def test_close(self, mock_init_list, mock_push_obj, mock_eval_obj, connection):
        connection.close()
        assert connection.is_closed is True
        assert connection.disposed_at is not None
        mock_eval_obj.assert_called_once()

    def test_context_manager(self, connection):
        with patch.object(connection, "close") as mock_close:
            with connection:
                pass
            mock_close.assert_called_once()


class TestKDBEngine:
    @pytest.fixture
    def engine(self):
        return KDBEngine(host="localhost", port=5000)

    @pytest.fixture
    def engine_no_port(self):
        return KDBEngine(host="localhost:5000")

    def test_init_with_port(self, engine):
        assert engine.url == "localhost:5000"
        assert engine.pool == {}

    def test_init_without_port(self, engine_no_port):
        assert engine_no_port.url == "localhost:5000"
        assert engine_no_port.pool == {}

    @patch("rayforce.plugins.raykx.FFI.eval_obj")
    @patch("rayforce.plugins.raykx.FFI.push_obj")
    @patch("rayforce.plugins.raykx.FFI.init_string")
    @patch("rayforce.plugins.raykx.FFI.init_list")
    def test_acquire_success(
        self, mock_init_list, mock_init_string, mock_push_obj, mock_eval_obj, engine
    ):
        mock_conn = MagicMock(spec=r.RayObject)
        mock_conn.get_obj_type.return_value = -r.TYPE_I64
        mock_eval_obj.return_value = mock_conn

        conn = engine.acquire()
        assert isinstance(conn, KDBConnection)
        assert conn.engine == engine
        assert conn.ptr == mock_conn
        assert id(conn) in engine.pool

    @patch("rayforce.plugins.raykx.FFI.eval_obj")
    @patch("rayforce.plugins.raykx.FFI.get_error_obj")
    @patch("rayforce.plugins.raykx.FFI.push_obj")
    @patch("rayforce.plugins.raykx.FFI.init_string")
    @patch("rayforce.plugins.raykx.FFI.init_list")
    def test_acquire_failure(
        self, mock_init_list, mock_init_string, mock_push_obj, mock_get_error, mock_eval_obj, engine
    ):
        mock_error = MagicMock(spec=r.RayObject)
        mock_error.get_obj_type.return_value = r.TYPE_ERR
        mock_eval_obj.return_value = mock_error
        mock_get_error.return_value = "Connection failed"

        with pytest.raises(ValueError, match="Error when establishing connection"):
            engine.acquire()

    @patch("rayforce.plugins.raykx.FFI.eval_obj")
    @patch("rayforce.plugins.raykx.FFI.push_obj")
    @patch("rayforce.plugins.raykx.FFI.init_string")
    @patch("rayforce.plugins.raykx.FFI.init_list")
    def test_dispose_connections(
        self, mock_init_list, mock_init_string, mock_push_obj, mock_eval_obj, engine
    ):
        mock_conn1 = MagicMock(spec=r.RayObject)
        mock_conn1.get_obj_type.return_value = -r.TYPE_I64
        mock_conn2 = MagicMock(spec=r.RayObject)
        mock_conn2.get_obj_type.return_value = -r.TYPE_I64
        mock_eval_obj.side_effect = [mock_conn1, mock_conn2]

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
