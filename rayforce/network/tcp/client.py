from __future__ import annotations

import contextlib
import typing as t

from rayforce import errors
from rayforce.ffi import FFI
from rayforce.network import utils
from rayforce.utils import ray_to_python


class TCPClient:
    """Synchronous client for a Rayforce IPC server (v2 native protocol)."""

    def __init__(
        self,
        host: str,
        port: int,
        *,
        user: str = "",
        password: str = "",
    ) -> None:
        utils.validate_port(port)
        self.host = host
        self.port = port
        self._handle = FFI.ipc_connect(host, port, user, password)
        self._alive = True

    @property
    def url(self) -> str:
        return f"{self.host}:{self.port}"

    def execute(self, data: t.Any) -> t.Any:
        if not self._alive:
            raise errors.RayforceTCPError("Cannot send on a closed connection")
        return ray_to_python(FFI.ipc_send(self._handle, utils.python_to_ipc(data)))

    def send_async(self, data: t.Any) -> None:
        if not self._alive:
            raise errors.RayforceTCPError("Cannot send on a closed connection")
        FFI.ipc_send_async(self._handle, utils.python_to_ipc(data))

    def close(self) -> None:
        if not self._alive:
            return
        FFI.ipc_close(self._handle)
        self._alive = False

    def __enter__(self) -> TCPClient:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __del__(self) -> None:
        with contextlib.suppress(Exception):
            self.close()

    def __repr__(self) -> str:
        return f"TCPClient({self.url}) - alive: {self._alive}"
