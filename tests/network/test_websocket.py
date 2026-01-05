from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import asyncio

from rayforce import _rayforce_c as r, I64, Vector, U8, String
from rayforce import errors
from rayforce.network.websocket import WebSocketServer, WebSocketConnection


class TestWebSocketServer:
    @pytest.fixture
    def server(self):
        return WebSocketServer(port=5000)

    @pytest.mark.parametrize("port", (0, 65536, -1))
    def test_init_invalid_port(self, port):
        with pytest.raises(errors.RayforceIPCError, match="Invalid port number"):
            WebSocketServer(port=port)

    @pytest.mark.asyncio
    async def test_stop(self, server):
        mock_server = AsyncMock()
        mock_server.close = MagicMock()
        mock_server.wait_closed = AsyncMock()
        server._server = mock_server
        server._connections = {
            "conn1": AsyncMock(spec=WebSocketConnection),
            "conn2": AsyncMock(spec=WebSocketConnection),
        }

        await server.stop()

        mock_server.close.assert_called_once()
        mock_server.wait_closed.assert_called_once()
        assert len(server._connections) == 0

    @pytest.mark.asyncio
    async def test_handle_connection(self, server):
        mock_websocket = AsyncMock()
        mock_websocket.remote_address = ("127.0.0.1", 12345)
        mock_websocket.__aiter__ = AsyncMock(return_value=iter([]))

        connection_mock = AsyncMock(spec=WebSocketConnection)
        connection_mock.handle = AsyncMock()
        connection_mock.close = AsyncMock()

        with patch("rayforce.network.websocket.WebSocketConnection", return_value=connection_mock):
            await server._handle_connection(mock_websocket)

        connection_mock.handle.assert_called_once()
        connection_mock.close.assert_called_once()
        assert len(server._connections) == 0

    @pytest.mark.asyncio
    async def test_handle_connection_error(self, server):
        mock_websocket = AsyncMock()
        mock_websocket.remote_address = ("127.0.0.1", 12345)

        connection_mock = AsyncMock(spec=WebSocketConnection)
        connection_mock.handle = AsyncMock(side_effect=RuntimeError("Test error"))
        connection_mock.close = AsyncMock()

        with patch("rayforce.network.websocket.WebSocketConnection", return_value=connection_mock):
            await server._handle_connection(mock_websocket)

        connection_mock.close.assert_called_once()
        assert len(server._connections) == 0

    @pytest.mark.asyncio
    async def test_run_stops_on_signal(self, server):
        mock_server = MagicMock()
        mock_server.close = MagicMock()
        mock_server.wait_closed = AsyncMock()
        mock_stop = asyncio.Future()
        mock_serve = AsyncMock(return_value=mock_server)

        with patch("rayforce.network.websocket.serve", mock_serve):
            with patch("rayforce.network.websocket.asyncio.get_event_loop") as mock_get_loop:
                mock_loop = MagicMock()
                mock_loop.create_future.return_value = mock_stop
                mock_loop.add_signal_handler = MagicMock()
                mock_get_loop.return_value = mock_loop

                run_task = asyncio.create_task(server.run())
                mock_stop.set_result(None)

                try:
                    await asyncio.wait_for(run_task, timeout=0.1)
                except asyncio.TimeoutError:
                    run_task.cancel()
                    try:
                        await run_task
                    except asyncio.CancelledError:
                        pass


class TestWebSocketConnection:
    @pytest.fixture
    def connection(self):
        websocket = AsyncMock()
        websocket.send = AsyncMock()
        websocket.close = AsyncMock()
        websocket.__aiter__ = AsyncMock(return_value=iter([]))
        return WebSocketConnection(websocket=websocket, server=MagicMock(spec=WebSocketServer))

    @pytest.mark.asyncio
    async def test_process_text_message_success(self, connection):
        mock_result = I64(42).ptr
        mock_string = String("(+ 1 2)")

        with patch("rayforce.network.websocket.String", return_value=mock_string):
            with patch("rayforce.network.websocket.FFI.eval_str", return_value=mock_result):
                with patch("rayforce.network.websocket.FFI.get_obj_type", return_value=r.TYPE_I64):
                    result = await connection._process_text_message("(+ 1 2)")

        assert result == mock_result

    @pytest.mark.asyncio
    async def test_process_text_message_eval_error(self, connection):
        error_obj = String("Eval failed").ptr

        with patch("rayforce.network.websocket.FFI.eval_str", return_value=error_obj):
            with patch(
                "rayforce.network.websocket.FFI.get_obj_type",
                side_effect=lambda x: r.TYPE_ERR if x is error_obj else r.TYPE_C8,
            ):
                with patch("rayforce.network.websocket.FFI.get_error_obj", return_value=error_obj):
                    with pytest.raises(errors.RayforceIPCError, match="Evaluation error"):
                        await connection._process_text_message("(+ 1 2)")

    @pytest.mark.asyncio
    async def test_process_binary_message_success(self, connection):
        mock_result = I64(42).ptr
        mock_deserialized = I64(10).ptr
        mock_vector = Vector(items=[1, 2, 3], ray_type=U8)
        call_count = [0]  # get_obj_type is called twice

        def get_obj_type_side_effect(_):
            call_count[0] += 1
            return r.TYPE_I64

        with patch("rayforce.network.websocket.Vector", return_value=mock_vector):
            with patch("rayforce.network.websocket.FFI.de_obj", return_value=mock_deserialized):
                with patch(
                    "rayforce.network.websocket.FFI.get_obj_type",
                    side_effect=get_obj_type_side_effect,
                ):
                    with patch("rayforce.network.websocket.FFI.eval_obj", return_value=mock_result):
                        result = await connection._process_binary_message(b"test_data")

        assert result == mock_result

    @pytest.mark.asyncio
    async def test_process_binary_message_deserialization_error(self, connection):
        mock_error = MagicMock(spec=r.RayObject)
        mock_vector = MagicMock()

        with patch("rayforce.network.websocket.Vector", return_value=mock_vector):
            with patch("rayforce.network.websocket.FFI.de_obj", return_value=mock_error):
                with patch(
                    "rayforce.network.websocket.FFI.get_obj_type",
                    side_effect=lambda x: r.TYPE_ERR if x is mock_error else r.TYPE_C8,
                ):
                    with patch("rayforce.network.websocket.FFI.get_error_obj", return_value="fail"):
                        with pytest.raises(errors.RayforceIPCError, match="fail"):
                            await connection._process_binary_message(b"test_data")

    @pytest.mark.asyncio
    async def test_send_result_success(self, connection):
        mock_result = I64(123).ptr
        mock_serialized = I64(456).ptr
        mock_bytes = b"serialized_data"

        with patch("rayforce.network.websocket.FFI.ser_obj", return_value=mock_serialized):
            with patch(
                "rayforce.network.websocket.FFI.get_obj_type",
                side_effect=lambda x: r.TYPE_U8 if x is mock_serialized else r.TYPE_I64,
            ):
                with patch(
                    "rayforce.network.websocket.FFI.read_u8_vector", return_value=mock_bytes
                ):
                    await connection._send_result(mock_result)

        connection.websocket.send.assert_called_once_with(mock_bytes)

    @pytest.mark.asyncio
    async def test_send_result_serialization_error(self, connection):
        mock_result = MagicMock(spec=r.RayObject)
        mock_error = MagicMock(spec=r.RayObject)

        with patch("rayforce.network.websocket.FFI.ser_obj", return_value=mock_error):
            with patch(
                "rayforce.network.websocket.FFI.get_obj_type",
                side_effect=lambda x: r.TYPE_ERR if x is mock_error else r.TYPE_C8,
            ):
                with patch("rayforce.network.websocket.FFI.get_error_obj", return_value="failed"):
                    await connection._send_result(mock_result)

        connection.websocket.send.assert_called_once()
        call_args = connection.websocket.send.call_args[0][0]
        assert b"error" in call_args.lower()

    @pytest.mark.asyncio
    async def test_send_error(self, connection):
        error_msg = "Test error message"
        await connection._send_error(error_msg)

        connection.websocket.send.assert_called_once()
        call_args = connection.websocket.send.call_args[0][0]
        assert b"error" in call_args.lower()
        assert error_msg.encode() in call_args

    @pytest.mark.asyncio
    async def test_send_error_handles_exception(self, connection):
        connection.websocket.send = AsyncMock(side_effect=Exception("Send failed"))
        await connection._send_error("Test error")  # Should not raise

    @pytest.mark.asyncio
    async def test_handle_text_message(self, connection):
        mock_result = MagicMock(spec=r.RayObject)
        connection._process_text_message = AsyncMock(return_value=mock_result)
        connection._send_result = AsyncMock()

        async def message_generator():
            yield "(+ 1 2)"

        connection.websocket.__aiter__ = lambda self: message_generator()
        await connection.handle()

        connection._process_text_message.assert_called_once_with("(+ 1 2)")
        connection._send_result.assert_called_once_with(mock_result)

    @pytest.mark.asyncio
    async def test_handle_binary_message(self, connection):
        mock_result = MagicMock(spec=r.RayObject)
        connection._process_binary_message = AsyncMock(return_value=mock_result)
        connection._send_result = AsyncMock()

        async def message_generator():
            yield b"binary_data"

        connection.websocket.__aiter__ = lambda self: message_generator()
        await connection.handle()

        connection._process_binary_message.assert_called_once_with(b"binary_data")
        connection._send_result.assert_called_once_with(mock_result)

    @pytest.mark.asyncio
    async def test_handle_message_error(self, connection):
        connection._process_text_message = AsyncMock(side_effect=RuntimeError("Processing error"))
        connection._send_error = AsyncMock()

        async def message_generator():
            yield "test"

        connection.websocket.__aiter__ = lambda self: message_generator()

        await connection.handle()

        connection._send_error.assert_called_once()
        assert "Processing error" in connection._send_error.call_args[0][0]

    @pytest.mark.asyncio
    async def test_handle_stops_when_closed(self, connection):
        connection._closed = True
        connection._process_text_message = AsyncMock()

        async def message_generator():
            yield "test1"
            yield "test2"

        connection.websocket.__aiter__ = lambda self: message_generator()
        await connection.handle()

        connection._process_text_message.assert_not_called()  # Should not process any messages

    @pytest.mark.asyncio
    async def test_close(self, connection):
        await connection.close()

        assert connection._closed is True
        assert connection.disposed_at is not None
        connection.websocket.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_handles_exception(self, connection):
        connection.websocket.close = AsyncMock(side_effect=Exception("Close failed"))
        await connection.close()  # Should not raise
        assert connection._closed is True
