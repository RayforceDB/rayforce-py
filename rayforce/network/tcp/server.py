from __future__ import annotations

import contextlib

from rayforce import errors
from rayforce.ffi import FFI
from rayforce.network import utils


class TCPServer:
    """Blocking Rayforce IPC server (v2 native protocol)."""

    DEFAULT_POLL_INTERVAL_MS = 100

    def __init__(self, port: int) -> None:
        utils.validate_port(port)
        self.port = port
        self._handle: int | None = None
        self._running = False

    def listen(self, *, poll_interval_ms: int = DEFAULT_POLL_INTERVAL_MS) -> None:
        if self._handle is not None:
            raise errors.RayforceTCPError("Server already listening")

        self._handle = FFI.ipc_server_init(self.port)
        self._running = True
        try:
            while self._running:
                FFI.ipc_server_poll(self._handle, poll_interval_ms)
        finally:
            self.close()

    def stop(self) -> None:
        self._running = False

    def close(self) -> None:
        self._running = False
        if self._handle is None:
            return
        with contextlib.suppress(Exception):
            FFI.ipc_server_destroy(self._handle)
        self._handle = None

    def __enter__(self) -> TCPServer:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __del__(self) -> None:
        with contextlib.suppress(Exception):
            self.close()

    def __repr__(self) -> str:
        state = "listening" if self._handle is not None else "idle"
        return f"TCPServer(port={self.port}, {state})"
