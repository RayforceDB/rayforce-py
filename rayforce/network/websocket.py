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
from rayforce.types.containers.vector import String, Vector
from rayforce.types.scalars.numeric.unsigned import U8

try:
    from websockets import Server, serve  # type: ignore[import-not-found]
except ImportError as e:
    raise ImportError(
        "websockets library is required. Install it with: pip install websockets"
    ) from e


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
        deserialized = FFI.de_obj(Vector(items=list(data), ray_type=U8).ptr)

        if FFI.get_obj_type(deserialized) == r.TYPE_ERR:
            raise errors.RayforceIPCError(
                f"Deserialization error: {FFI.get_error_obj(deserialized)}"
            )

        result = FFI.eval_obj(deserialized)

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
