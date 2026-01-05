from __future__ import annotations

import asyncio
import contextlib
from datetime import UTC, datetime
import json
import signal
import typing as t

from rayforce import _rayforce_c as r
from rayforce import errors
from rayforce.ffi import FFI
from rayforce.types.containers.list import List
from rayforce.types.containers.vector import String, Vector
from rayforce.types.operators import Operation
from rayforce.types.scalars.numeric.unsigned import U8
from rayforce.utils import ray_to_python

try:
    from websockets import Server, connect, serve  # type: ignore[import-not-found]
except ImportError as e:
    raise ImportError(
        "websockets library is required. Install it with: pip install websockets"
    ) from e


def _python_to_websocket(data: t.Any) -> r.RayObject:
    from rayforce.types.table import (
        Expression,
        InnerJoin,
        InsertQuery,
        LeftJoin,
        SelectQuery,
        UpdateQuery,
        UpsertQuery,
        WindowJoin,
        WindowJoin1,
    )

    if isinstance(data, str):
        return String(data).ptr
    if isinstance(data, List):
        return data.ptr
    if isinstance(data, SelectQuery):
        return Expression(Operation.SELECT, data.compile()).compile()
    if isinstance(data, UpdateQuery):
        return Expression(Operation.UPDATE, data.compile()).compile()
    if isinstance(data, InsertQuery):
        return Expression(Operation.INSERT, data.table, data.compile()).compile()
    if isinstance(data, UpsertQuery):
        return Expression(Operation.UPSERT, data.table, *data.compile()).compile()
    if isinstance(data, LeftJoin):
        return Expression(Operation.LEFT_JOIN, *data.compile()).compile()
    if isinstance(data, InnerJoin):
        return Expression(Operation.INNER_JOIN, *data.compile()).compile()
    if isinstance(data, WindowJoin):
        return Expression(Operation.WINDOW_JOIN, *data.compile()).compile()
    if isinstance(data, WindowJoin1):
        return Expression(Operation.WINDOW_JOIN1, *data.compile()).compile()
    raise errors.RayforceIPCError(f"Unsupported WebSocket data to send: {type(data)}")


class WebSocketServer:
    def __init__(self, port: int) -> None:
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise errors.RayforceIPCError(
                f"Invalid port number: {port}. Must be between 1 and 65535"
            )

        self.port = port
        self._server: Server | None = None
        self._connections: dict[str, WebSocketConnection] = {}

    async def start(self) -> None:
        self._server = await serve(self._handle_connection, "0.0.0.0", self.port)

    async def stop(self) -> None:
        if self._server:
            self._server.close()
            await self._server.wait_closed()

        for conn in list(self._connections.values()):
            await conn.close()
        self._connections.clear()
        print("\nRayforce WebSocket Server stopped.", flush=True)

    async def _handle_connection(self, websocket: t.Any) -> None:
        conn_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        connection = WebSocketConnection(websocket=websocket, server=self)
        self._connections[conn_id] = connection

        try:
            await connection.handle()
        except Exception as e:
            print(f"Connection {conn_id} error: {e}", flush=True)
        finally:
            self._connections.pop(conn_id, None)
            await connection.close()

    async def run(self) -> None:
        loop = asyncio.get_event_loop()
        stop = loop.create_future()

        def _stop():
            if not stop.done():
                stop.set_result(None)

        loop.add_signal_handler(signal.SIGINT, _stop)
        loop.add_signal_handler(signal.SIGTERM, _stop)
        await self.start()

        try:
            print(f"Rayforce WebSocket Server listening on 0.0.0.0:{self.port}", flush=True)
            await stop  # Run forever
        finally:
            await self.stop()

    def __repr__(self) -> str:
        return f"WebSocketServer(port={self.port})"


class WebSocketConnection:
    RAYFORCE_VERSION = 1

    def __init__(self, websocket: t.Any, server: WebSocketServer) -> None:
        self.websocket = websocket
        self.server = server
        self._closed = False
        self._handshake_complete = False
        self.established_at = datetime.now(UTC)
        self.disposed_at: datetime | None = None

    @staticmethod
    def _parse_handshake(handshake: bytes) -> None:
        if not isinstance(handshake, bytes):
            raise errors.RayforceIPCError(f"Expected binary handshake, got {type(handshake)}")

        if len(handshake) < 2:
            raise errors.RayforceIPCError(
                f"Invalid handshake length: expected 2 bytes, got {len(handshake)}"
            )

        _, null_byte = handshake[0], handshake[1]

        if null_byte != 0x00:
            raise errors.RayforceIPCError(
                f"Invalid handshake format: expected null terminator (0x00), got 0x{null_byte:02x}"
            )

    async def _perform_handshake(self) -> None:
        try:
            handshake = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            self._parse_handshake(handshake)
            await self.websocket.send(bytes([self.RAYFORCE_VERSION]))
            self._handshake_complete = True
        except TimeoutError as e:
            raise errors.RayforceIPCError("Handshake timeout: client did not send handshake") from e
        except Exception as e:
            if isinstance(e, errors.RayforceIPCError):
                raise
            raise errors.RayforceIPCError(f"Handshake error: {e}") from e

    async def handle(self) -> None:
        await self._perform_handshake()

        async for message in self.websocket:
            if self._closed:
                break

            try:
                if isinstance(message, bytes):  # binary
                    result = await self._process_binary_message(message)
                    if result is not None:
                        await self._send_result(result)

                elif isinstance(message, str):  # text
                    result = await self._process_text_message(message)
                    if result is not None:
                        await self._send_result(result)

            except Exception as e:
                error_msg = f"Error processing message: {e}"
                print(error_msg, flush=True)
                await self._send_error(error_msg)

    async def _process_binary_message(self, data: bytes) -> r.RayObject | None:
        deser = FFI.de_obj(Vector(items=list(data), ray_type=U8).ptr)

        obj_type = FFI.get_obj_type(deser)

        if obj_type == r.TYPE_ERR:
            raise errors.RayforceIPCError(f"Deserialization error: {FFI.get_error_obj(deser)}")

        result = FFI.eval_str(deser) if obj_type == r.TYPE_C8 else FFI.eval_obj(deser)
        if FFI.get_obj_type(result) == r.TYPE_ERR:
            raise errors.RayforceIPCError(f"Evaluation error: {FFI.get_error_obj(result)}")

        return result

    async def _process_text_message(self, message: str) -> r.RayObject | None:
        result = FFI.eval_str(String(message).ptr)

        if FFI.get_obj_type(result) == r.TYPE_ERR:
            raise errors.RayforceIPCError(f"Evaluation error: {FFI.get_error_obj(result)}")

        return result

    async def _send_result(self, result: r.RayObject) -> None:
        try:
            serialized = FFI.ser_obj(result)

            if FFI.get_obj_type(serialized) == r.TYPE_ERR:
                await self._send_error(f"Error serializing result: {FFI.get_error_obj(serialized)}")
                return

            await self.websocket.send(FFI.read_u8_vector(serialized))
        except Exception as e:
            await self._send_error(f"Error serializing result: {e}")

    async def _send_error(self, error_msg: str) -> None:
        with contextlib.suppress(Exception):
            await self.websocket.send(json.dumps({"error": error_msg}).encode("utf-8"))

    async def close(self) -> None:
        if not self._closed:
            self._closed = True
            self.disposed_at = datetime.now(UTC)

            with contextlib.suppress(Exception):
                await self.websocket.close()


class WebSocketClientConnection:
    RAYFORCE_VERSION = 1

    def __init__(self, websocket: t.Any, client: WebSocketClient) -> None:
        self.websocket = websocket
        self.client = client
        self._closed = False
        self._handshake_complete = False
        self.established_at = datetime.now(UTC)
        self.disposed_at: datetime | None = None

    @staticmethod
    def _parse_handshake(handshake: bytes) -> None:
        if not isinstance(handshake, bytes) or len(handshake) != 1:
            raise errors.RayforceIPCError(
                f"Invalid handshake response: expected 1 byte, got {type(handshake)}"
            )

    async def _perform_handshake(self) -> None:
        try:
            await self.websocket.send(bytes([self.RAYFORCE_VERSION, 0x00]))
            handshake = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            self._parse_handshake(handshake)
            self._handshake_complete = True
        except TimeoutError as e:
            raise errors.RayforceIPCError("Handshake timeout: server did not respond") from e
        except Exception as e:
            if isinstance(e, errors.RayforceIPCError):
                raise
            raise errors.RayforceIPCError(f"Handshake error: {e}") from e

    async def execute(self, data: t.Any) -> t.Any:
        if self._closed:
            raise errors.RayforceIPCError("Cannot execute on closed connection")
        if not self._handshake_complete:
            raise errors.RayforceIPCError("Handshake not completed")

        serialized = FFI.ser_obj(_python_to_websocket(data))

        if FFI.get_obj_type(serialized) == r.TYPE_ERR:
            raise errors.RayforceIPCError(f"Serialization error: {FFI.get_error_obj(serialized)}")

        binary_data = FFI.read_u8_vector(serialized)
        await self.websocket.send(binary_data)

        response = await self.websocket.recv()
        if not isinstance(response, bytes):
            if isinstance(response, str):
                try:
                    error_data = json.loads(response)
                    if "error" in error_data:
                        raise errors.RayforceIPCError(f"Server error: {error_data['error']}")
                except json.JSONDecodeError:
                    pass
            raise errors.RayforceIPCError(f"Expected binary response, got {type(response)}")

        response_vector = Vector(items=list(response), ray_type=U8).ptr
        deserialized = FFI.de_obj(response_vector)

        if FFI.get_obj_type(deserialized) == r.TYPE_ERR:
            raise errors.RayforceIPCError(
                f"Deserialization error: {FFI.get_error_obj(deserialized)}"
            )

        return ray_to_python(deserialized)

    async def close(self) -> None:
        if not self._closed:
            self._closed = True
            self.disposed_at = datetime.now(UTC)

            with contextlib.suppress(Exception):
                await self.websocket.close()

            if hasattr(self.client, "pool"):
                self.client.pool.pop(id(self), None)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    def __repr__(self) -> str:
        if self._closed:
            return (
                f"WebSocketConnection(id:{id(self)}) - "
                f"disposed at {self.disposed_at.isoformat() if self.disposed_at else 'Unknown'}"
            )
        return (
            f"WebSocketConnection(id:{id(self)}) - established at {self.established_at.isoformat()}"
        )


class WebSocketClient:
    def __init__(self, host: str, port: int) -> None:
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise errors.RayforceIPCError(
                f"Invalid port number: {port}. Must be between 1 and 65535"
            )

        self.host = host
        self.port = port
        self.uri = f"ws://{host}:{port}"
        self.pool: dict[int, WebSocketClientConnection] = {}

    async def acquire(self) -> WebSocketClientConnection:
        websocket = await connect(self.uri)
        connection = WebSocketClientConnection(websocket=websocket, client=self)
        await connection._perform_handshake()
        self.pool[id(connection)] = connection
        return connection

    async def dispose_connections(self) -> None:
        connections = list(self.pool.values())
        for conn in connections:
            await conn.close()
        self.pool = {}

    def __repr__(self) -> str:
        return f"WebSocketClient(host={self.host}, port={self.port}, pool_size: {len(self.pool)})"
