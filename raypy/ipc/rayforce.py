from __future__ import annotations
from datetime import datetime
import typing as t

from raypy import api
from raypy import types
from raypy import _rayforce as r


class ConnectionAlreadyClosed(Exception):
    """Raises when attemting to utilise closed connection"""


class RayforceConnection:
    ptr: r.RayObject
    _type = -r.TYPE_I64  # Descriptor

    def __init__(
        self,
        pool: "RayforceConnectionPool",
        conn: r.RayObject,
    ) -> None:
        if (_type := conn.get_obj_type()) != self._type:
            raise ValueError(
                f"Invalid KDB connection object type. Expected {self._type}, got {_type}"
            )

        self.pool = pool
        self.ptr = conn
        self.established_at = datetime.now()
        self.disposed_at: datetime | None = None
        self.is_closed = False

    def __execute_rf_query(self, query: r.RayObject) -> r.RayObject:
        return api.write(self.ptr, query)

    def __close_rf_connection(self) -> r.RayObject:
        return api.hclose(self.ptr)

    def execute(self, query: t.Any) -> r.RayObject:
        if self.is_closed:
            raise ConnectionAlreadyClosed()

        result = self.__execute_rf_query(
            query=types.from_python_type_to_raw_rayobject(query, is_ipc=True),
        )
        if result.get_obj_type() == r.TYPE_ERR:
            error_message = api.get_error_message(result)
            if error_message and error_message.startswith("'ipc_send"):
                raise ConnectionAlreadyClosed()

            raise ValueError(f"Failed to execute statement: {error_message}")

        return types.convert_raw_rayobject_to_raypy_type(result)

    def close(self) -> None:
        self.__close_rf_connection()
        self.is_closed = True
        self.disposed_at = datetime.now()

    def __enter__(self) -> "RayforceConnection":
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.close()

    def __repr__(self) -> str:
        if self.is_closed:
            return f"RayforceConnection(id:{id(self)}) - disposed at {self.disposed_at.isoformat() if self.disposed_at else 'Unknown'}"
        return f"RayforceConnection(id:{id(self)}) - established at {self.established_at.isoformat()}"


class RayforceConnectionPool:
    pool: dict[int, RayforceConnection] = {}

    def __init__(
        self,
        host: str,
        port: int | None = None,
        timeout: int = 60,
    ) -> None:
        self.url = f"{host}:{port}" if port is not None else host
        self.timeout = timeout

    def __open_rf_connection(self) -> r.RayObject:
        host = api.init_string(self.url)
        timeout = api.init_i64(self.timeout)
        return api.hopen(host, timeout)

    def acquire(self) -> RayforceConnection:
        _conn = self.__open_rf_connection()
        if _conn.get_obj_type() == r.TYPE_ERR:
            raise ValueError(
                f"Error when establishing connection: {api.get_error_message(_conn)}"
            )

        conn = RayforceConnection(pool=self, conn=_conn)
        self.pool[id(conn)] = conn
        return conn

    def dispose_connections(self) -> None:
        connections = self.pool.values()
        for conn in connections:
            conn.close()
        self.pool = {}

    def __repr__(self) -> str:
        return f"RayforceConnectionPool(pool_size: {len(self.pool)})"
