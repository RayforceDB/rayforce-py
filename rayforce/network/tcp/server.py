from __future__ import annotations

import contextlib

from rayforce import errors
from rayforce.ffi import FFI


class TCPServer:
    def __init__(self, port: int) -> None:
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise errors.RayforceTCPError(f"Invalid port: {port}. Must be between 1 and 65535")

        self.port = port
        self._listener_id: int | None = None

    def listen(self) -> None:
        self._listener_id = FFI.ipc_listen(self.port)
        print(f"Rayforce IPC Server listening on {self.port} (id:{self._listener_id})", flush=True)

        try:
            FFI.runtime_run()  # Start blocking event loop
        except BaseException:
            if self._listener_id is not None:
                with contextlib.suppress(Exception):
                    FFI.ipc_close_listener(self._listener_id)
                self._listener_id = None
            raise

    def __repr__(self) -> str:
        return f"TCPServer(port={self.port})"
