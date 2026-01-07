from __future__ import annotations

import contextlib
import typing as t

from rayforce import _rayforce_c as r
from rayforce import errors
from rayforce.ffi import FFI
from rayforce.network import utils
from rayforce.types.containers.vector import String
from rayforce.utils import ray_to_python


class TCPClient:
    def __init__(self, host: str, port: int | None = None) -> None:
        self._alive = True
        self.url = f"{host}:{port}" if port is not None else host
        self.handle = FFI.hopen(String(self.url).ptr)
        if FFI.get_obj_type(self.handle) == r.TYPE_ERR:
            error_message = FFI.get_error_obj(self.handle)
            raise errors.RayforceTCPError(f"Error when establishing connection: {error_message}")

    def execute(self, data: t.Any) -> t.Any:
        if not self._alive:
            raise errors.RayforceTCPError("Cannot write to closed connection")
        return ray_to_python(FFI.write(self.handle, utils.python_to_ipc(data)))

    def close(self) -> None:
        if not self._alive:
            return

        FFI.hclose(self.handle)
        self._alive = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __del__(self) -> None:
        with contextlib.suppress(Exception):
            self.close()

    def __repr__(self) -> str:
        return f"TCPClient({self.url}) - alive: {self._alive}"
