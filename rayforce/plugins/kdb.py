from __future__ import annotations

import contextlib
from datetime import UTC, datetime
import weakref

from rayforce import _rayforce_c as r
from rayforce import utils
from rayforce.ffi import FFI
from rayforce.plugins import errors


def _error_message(err_result: r.RayObject) -> str:
    """Decode a core TYPE_ERR object's `message` field to a plain string."""
    from rayforce import Dict

    error = Dict(ptr=FFI.get_error_obj(err_result))
    message = error["message"]
    return str(getattr(message, "value", message))


class KDBConnection:
    def __init__(self, handle: int) -> None:
        self._handle = handle
        self.established_at = datetime.now(UTC)
        self.disposed_at: datetime | None = None
        self.is_closed = False

    def execute(self, query: str) -> object:
        if self.is_closed:
            raise errors.KDBConnectionAlreadyClosedError
        try:
            result = r.kdb_send(self._handle, FFI.init_string(query))
        except RuntimeError as exc:
            # kdb_send raises (not a TYPE_ERR return) on a send/recv-level failure.
            msg = str(exc)
            if "closed" in msg.lower() or "ipc_send" in msg:
                raise errors.KDBConnectionAlreadyClosedError("Connection already closed.") from exc
            raise errors.KDBConnectionError(f"Failed to execute statement: {msg}") from exc
        if FFI.get_obj_type(result) == r.TYPE_ERR:
            # get_error_obj returns a {code, message} dict, not a string.
            msg = _error_message(result)
            if "ipc_send" in msg or "closed" in msg.lower():
                raise errors.KDBConnectionAlreadyClosedError("Connection already closed.")
            raise errors.KDBConnectionError(f"Failed to execute statement: {msg}")
        return utils.ray_to_python(result)

    def close(self) -> None:
        if self.is_closed:
            return
        with contextlib.suppress(Exception):
            r.kdb_close(self._handle)
        self.is_closed = True
        self.disposed_at = datetime.now(UTC)

    def __enter__(self) -> KDBConnection:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __repr__(self) -> str:
        if self.is_closed:
            ts = self.disposed_at.isoformat() if self.disposed_at else "Unknown"
            return f"KDBConnection(id:{id(self)}) - disposed at {ts}"
        return f"KDBConnection(id:{id(self)}) - established at {self.established_at.isoformat()}"


class KDBEngine:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.pool: weakref.WeakValueDictionary[int, KDBConnection] = weakref.WeakValueDictionary()

    @property
    def url(self) -> str:
        return f"{self.host}:{self.port}"

    def acquire(self) -> KDBConnection:
        try:
            handle = r.kdb_connect(self.host, self.port)
        except RuntimeError as exc:
            raise errors.KDBConnectionError(f"Error when establishing connection: {exc}") from exc
        conn = KDBConnection(handle=handle)
        self.pool[id(conn)] = conn
        return conn

    def dispose_connections(self) -> None:
        for conn in list(self.pool.values()):
            conn.close()
        self.pool.clear()

    def __repr__(self) -> str:
        return f"KDBEngine({self.url}, pool_size: {len(self.pool)})"
