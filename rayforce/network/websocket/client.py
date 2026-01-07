from __future__ import annotations

import asyncio
import contextlib
import typing as t

from rayforce import Dict, errors
from rayforce import _rayforce_c as r
from rayforce.ffi import FFI
from rayforce.network import utils
from rayforce.network.websocket import constants
from rayforce.types.containers.vector import Vector
from rayforce.types.scalars.numeric.unsigned import U8
from rayforce.utils import ray_to_python

try:
    from websockets import (  # type: ignore[import-not-found]
        ClientConnection,
        ConnectionClosed,
        connect,
    )
except ImportError as e:
    raise ImportError(
        "websockets library is required. Install it with: pip install websockets"
    ) from e


class WSClientConnection:
    def __init__(self, ws: ClientConnection) -> None:
        self.ws = ws
        self._closed = False

    @staticmethod
    def _validate_handshake_response(handshake: bytes | str) -> None:
        if not isinstance(handshake, bytes):
            raise errors.RayforceWSError(
                f"Expected binary handshake response, got {type(handshake)}"
            )
        if len(handshake) != 1:
            raise errors.RayforceWSError(
                f"Invalid handshake response: expected 1 byte, got {len(handshake)} bytes"
            )

    async def _perform_handshake(self) -> None:
        try:
            await self.ws.send(bytes([constants.RAYFORCE_VERSION, 0x00]))  # [version, 0x00]
            handshake = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
            self._validate_handshake_response(handshake)
        except TimeoutError as e:
            raise errors.RayforceWSError("Handshake timeout: server did not respond") from e
        except errors.RayforceWSError:
            raise
        except Exception as e:
            raise errors.RayforceWSError(f"Handshake error: {e}") from e

    async def execute(self, data: t.Any) -> t.Any:
        if self._closed:
            raise errors.RayforceWSError("Cannot execute on closed connection")

        serialized = FFI.ser_obj(utils.python_to_ipc(data))
        if FFI.get_obj_type(serialized) == r.TYPE_ERR:
            raise errors.RayforceWSError(f"Serialization error: {FFI.get_error_obj(serialized)}")

        try:
            await self.ws.send(FFI.read_u8_vector(serialized))
            response = await self.ws.recv()
        except ConnectionClosed as e:
            self._closed = True
            raise errors.RayforceWSError(f"Connection closed: {e}") from e

        if not isinstance(response, bytes):
            raise errors.RayforceWSError(f"Expected binary response, got {type(response)}")

        deserialized = FFI.de_obj(Vector(items=list(response), ray_type=U8).ptr)
        if FFI.get_obj_type(deserialized) == r.TYPE_ERR:
            error = Dict(ptr=FFI.get_error_obj(deserialized))
            raise errors.CORE_EXC_CODE_MAPPING.get(
                error["code"].value, errors.RayforceUserError
            ).serialize(error)

        return ray_to_python(deserialized)

    async def close(self) -> None:
        if not self._closed:
            self._closed = True
            with contextlib.suppress(Exception):
                await self.ws.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    def __repr__(self) -> str:
        status = "closed" if self._closed else "open"
        return f"WSClientConnection({status})"


class WSClient:
    def __init__(self, host: str, port: int | None = None) -> None:
        if port is not None:
            utils.validate_port(port)
        self.uri = f"ws://{host}:{port}" if port is not None else f"ws://{host}"

    async def connect(self) -> WSClientConnection:
        try:
            ws = await connect(
                uri=self.uri,
                ping_interval=constants.WS_PING_INTERVAL,
                ping_timeout=constants.WS_PING_TIMEOUT,
                close_timeout=constants.WS_CLOSE_TIMEOUT,
            )
        except OSError as e:
            raise errors.RayforceWSError(f"Failed to connect to {self.uri}: {e}") from e
        except Exception as e:
            raise errors.RayforceWSError(f"Connection error: {e}") from e

        connection = WSClientConnection(ws=ws)
        await connection._perform_handshake()
        return connection

    def __repr__(self) -> str:
        return f"WSClient({self.uri})"
