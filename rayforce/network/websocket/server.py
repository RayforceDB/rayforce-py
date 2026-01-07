from __future__ import annotations

import asyncio
import contextlib
import signal
import typing as t

from rayforce import _rayforce_c as r
from rayforce import errors
from rayforce.ffi import FFI
from rayforce.network import utils
from rayforce.network.websocket import constants
from rayforce.types.containers.vector import Vector
from rayforce.types.scalars.numeric.unsigned import U8

try:
    from websockets import (  # type: ignore[import-not-found]
        ClientConnection,
        ConnectionClosed,
        Server,
        serve,
    )
except ImportError as e:
    raise ImportError(
        "websockets library is required. Install it with: pip install websockets"
    ) from e


class WSServer:
    def __init__(self, port: int) -> None:
        utils.validate_port(port)
        self.port = port
        self._server: Server | None = None
        self._connections: dict[str, WSServerConnection] = {}

    async def start(self) -> None:
        self._server = await serve(
            handler=self._handle_connection,
            host="0.0.0.0",
            port=self.port,
            ping_interval=constants.WS_PING_INTERVAL,
            ping_timeout=constants.WS_PING_TIMEOUT,
            close_timeout=constants.WS_CLOSE_TIMEOUT,
        )
        print(f"Rayforce WebSocket served on ws://0.0.0.0:{self.port}", flush=True)

    async def stop(self) -> None:
        if not self._server:
            raise errors.RayforceWSError("Server not started")

        # Close all connections before shutting down
        for conn in list(self._connections.values()):
            await conn.close()

        self._server.close()
        await self._server.wait_closed()
        self._server = None

        self._connections.clear()
        print("\nRayforce WebSocket Server stopped.", flush=True)

    async def _handle_connection(self, ws: t.Any) -> None:
        conn_id = f"{ws.remote_address[0]}:{ws.remote_address[1]}"
        connection = WSServerConnection(ws=ws)
        self._connections[conn_id] = connection

        try:
            await connection.handle()
        except ConnectionClosed:
            pass
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
        await stop  # Run forever

        await self.stop()

    def __repr__(self) -> str:
        return f"WSServer(port={self.port})"


class WSServerConnection:
    def __init__(self, ws: ClientConnection) -> None:
        self.ws = ws

    @staticmethod
    def _validate_handshake(handshake: bytes | str) -> None:
        if not isinstance(handshake, bytes):
            raise errors.RayforceWSError(f"Expected binary handshake, got {type(handshake)}")
        if len(handshake) < 2:
            raise errors.RayforceWSError(f"Expected 2 bytes handshake, got {len(handshake)}")
        if handshake[1] != 0x00:
            raise errors.RayforceWSError(f"Expected (0x00), got 0x{handshake[1]:02x}")

    async def _handshake(self) -> None:
        try:
            handshake = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
            self._validate_handshake(handshake)
            await self.ws.send(bytes([constants.RAYFORCE_VERSION]))
        except Exception as e:
            raise errors.RayforceWSError(f"Handshake error: {e}") from e

    async def handle(self) -> None:
        await self._handshake()

        try:
            async for message in self.ws:
                try:
                    await self._process_message(message)
                except ConnectionClosed:
                    break
                except Exception as e:
                    print(f"Error processing message: {e}", flush=True)
                    # Try to send error response to client instead of closing connection
                    # If we can't send, then break and close connection
                    try:
                        from rayforce.types.containers.vector import String

                        error_obj = String(str(e)).ptr
                        await self._send_result(error_obj)
                    except Exception as send_error:
                        print(f"Error sending error response: {send_error}", flush=True)
                        break
        except ConnectionClosed:
            pass
        except Exception as e:
            print(f"Connection error: {e}", flush=True)

    async def _process_message(self, message: bytes | str) -> None:
        if not isinstance(message, bytes):
            raise errors.RayforceWSError(f"Expected binary message, got {type(message)}")

        deser = FFI.de_obj(Vector(items=list(message), ray_type=U8).ptr)

        obj_type = FFI.get_obj_type(deser)
        match obj_type:
            case r.TYPE_ERR:
                result = deser
            case r.TYPE_C8:
                result = FFI.eval_str(deser)
            case _:
                result = FFI.eval_obj(deser)

        await self._send_result(result)

    async def _send_result(self, result: r.RayObject) -> None:
        serialized = FFI.ser_obj(result)
        if FFI.get_obj_type(serialized) == r.TYPE_ERR:
            print(f"Error serializing result: {FFI.get_error_obj(serialized)}", flush=True)
            return

        try:
            await self.ws.send(FFI.read_u8_vector(serialized))
        except Exception as e:
            print(f"Error sending result: {e}", flush=True)

    async def close(self) -> None:
        with contextlib.suppress(Exception):
            await self.ws.close()
