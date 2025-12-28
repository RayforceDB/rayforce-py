from __future__ import annotations

import contextlib
from datetime import UTC, datetime
import typing as t

from rayforce import _rayforce_c as r
from rayforce import errors
from rayforce.ffi import FFI
from rayforce.types.containers.vector import String
from rayforce.types.operators import Operation
from rayforce.utils import ray_to_python


def _python_to_ipc(data: t.Any) -> r.RayObject:
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
    if isinstance(data, SelectQuery):
        return Expression(Operation.LIST, Operation.SELECT, data.compile()).compile()
    if isinstance(data, UpdateQuery):
        return Expression(Operation.LIST, Operation.UPDATE, data.compile()).compile()
    if isinstance(data, InsertQuery):
        return Expression(Operation.LIST, Operation.INSERT, data.compile()).compile()
    if isinstance(data, UpsertQuery):
        return Expression(Operation.LIST, Operation.UPSERT, *data.compile()).compile()
    if isinstance(data, LeftJoin):
        return Expression(Operation.LIST, Operation.LEFT_JOIN, *data.compile()).compile()
    if isinstance(data, InnerJoin):
        return Expression(Operation.LIST, Operation.INNER_JOIN, *data.compile()).compile()
    if isinstance(data, WindowJoin):
        return Expression(Operation.LIST, Operation.WINDOW_JOIN, *data.compile()).compile()
    if isinstance(data, WindowJoin1):
        return Expression(Operation.LIST, Operation.WINDOW_JOIN1, *data.compile()).compile()
    raise errors.RayforceIPCError(f"Unsupported IPC data to send: {type(data)}")


class IPCConnection:
    def __init__(self, engine: IPCEngine, handle: r.RayObject) -> None:
        self.engine = engine
        self.handle = handle
        self._closed = False
        self.established_at = datetime.now(UTC)
        self.disposed_at: datetime | None = None

    def execute(self, data: t.Any) -> t.Any:
        if self._closed:
            raise errors.RayforceIPCError("Cannot write to closed connection")
        return ray_to_python(FFI.write(self.handle, _python_to_ipc(data)))

    def close(self) -> None:
        if not self._closed:
            FFI.hclose(self.handle)
            self._closed = True
            self.disposed_at = datetime.now(UTC)

            if hasattr(self.engine, "pool"):
                self.engine.pool.pop(id(self), None)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __del__(self) -> None:
        if not self._closed:
            with contextlib.suppress(Exception):
                self.close()

    def __repr__(self) -> str:
        if self._closed:
            return f"Connection(id:{id(self)}) - disposed at {self.disposed_at.isoformat() if self.disposed_at else 'Unknown'}"
        return f"Connection(id:{id(self)}) - established at {self.established_at.isoformat()}"


class IPCEngine:
    def __init__(self, host: str, port: int | None = None) -> None:
        self.host = host
        self.port = port
        self.url = f"{host}:{port}" if port is not None else host
        self.pool: dict[int, IPCConnection] = {}

    def __open_connection(self) -> r.RayObject:
        path = String(self.url)
        return FFI.hopen(path.ptr)

    def acquire(self) -> IPCConnection:
        handle = self.__open_connection()
        if FFI.get_obj_type(handle) == r.TYPE_ERR:
            error_message = FFI.get_error_obj(handle)
            raise errors.RayforceIPCError(f"Error when establishing connection: {error_message}")

        conn = IPCConnection(engine=self, handle=handle)
        self.pool[id(conn)] = conn
        return conn

    def dispose_connections(self) -> None:
        connections = list(self.pool.values())
        for conn in connections:
            conn.close()
        self.pool = {}

    def __repr__(self) -> str:
        return f"IPCEngine(host={self.host}, port={self.port}, pool_size: {len(self.pool)})"
