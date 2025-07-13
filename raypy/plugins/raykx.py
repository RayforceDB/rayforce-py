import sys
import os
from datetime import datetime

from raypy import api
from raypy import _rayforce as r
from raypy import types

if sys.platform == "darwin":
    raykx_lib_name = "libraykx.dylib"
elif sys.platform == "win32":
    raykx_lib_name = "libraykx.dll"
else:
    raykx_lib_name = "libraykx.so"

# Construct the path to the lib file relative to this directory
c_plugin_compiled_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), raykx_lib_name
)


# (.kx.hopen "127.0.0.1:5101")
_fn_hopen = api.loadfn_from_file(
    filename=c_plugin_compiled_path,
    fn_name="raykx_hopen",
    args_count=1,
)
# (.kx.hclose h)
_fn_hclose = api.loadfn_from_file(
    filename=c_plugin_compiled_path,
    fn_name="raykx_hclose",
    args_count=1,
)
# (.kx.send h "1+2")
_fn_send = api.loadfn_from_file(
    filename=c_plugin_compiled_path,
    fn_name="raykx_send",
    args_count=2,
)


class ConnectionAlreadyClosed(Exception):
    """Raises when attemting to utilise closed connection"""


class KDBConnection:
    ptr: r.RayObject
    _type = -r.TYPE_I64  # Descriptor

    def __init__(
        self,
        engine: "KDBEngine",
        conn: r.RayObject,
    ) -> None:
        if (_type := conn.get_obj_type()) != self._type:
            raise ValueError(
                f"Invalid KDB connection object type. Expected {self._type}, got {_type}"
            )

        self.engine = engine
        self.ptr = conn
        self.established_at = datetime.now()
        self.disposed_at: datetime | None = None
        self.is_closed = False

    def __execute_kdb_query(self, query: str) -> r.RayObject:
        # obj = types.List([_fn_send, self.ptr, query]).ptr
        obj = api.init_list()
        api.push_obj(obj, _fn_send)
        api.push_obj(obj, self.ptr)
        api.push_obj(obj, api.init_string(query))
        return api.eval_obj(obj)

    def __close_kdb_connection(self) -> r.RayObject:
        obj = api.init_list()
        api.push_obj(obj, _fn_hclose)
        api.push_obj(obj, self.ptr)
        api.eval_obj(obj)

    def execute(self, query: str) -> r.RayObject:
        if self.is_closed:
            raise ConnectionAlreadyClosed()

        result = self.__execute_kdb_query(query=query)
        if result.get_obj_type() == r.TYPE_ERR:
            error_message = api.get_error_message(result)
            if error_message and error_message.startswith("'ipc_send"):
                raise ConnectionAlreadyClosed()

            raise ValueError(f"Failed to execute statement: {error_message}")

        return types.convert_raw_rayobject_to_raypy_type(result)

    def close(self) -> None:
        self.__close_kdb_connection()
        self.is_closed = True
        self.disposed_at = datetime.now()

    def __enter__(self) -> "KDBConnection":
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.close()

    def __repr__(self) -> str:
        if self.is_closed:
            return f"KDBConnection(id:{id(self)}) - disposed at {self.disposed_at.isoformat() if self.disposed_at else 'Unknown'}"
        return f"KDBConnection(id:{id(self)}) - established at {self.established_at.isoformat()}"


class KDBEngine:
    pool: dict[int, KDBConnection] = {}

    def __init__(self, host: str, port: int | None = None) -> None:
        self.url = f"{host}:{port}" if port is not None else host

    def __open_kdb_connection(self) -> r.RayObject:
        host = api.init_string(self.url)
        obj = api.init_list()
        api.push_obj(obj, _fn_hopen)
        api.push_obj(obj, host)
        return api.eval_obj(obj)

    def acquire(self) -> KDBConnection:
        conn = self.__open_kdb_connection()
        if conn.get_obj_type() == r.TYPE_ERR:
            raise ValueError(
                f"Error when establishing connection: {api.get_error_message(conn)}"
            )

        conn = KDBConnection(engine=self, conn=self.__open_kdb_connection())
        self.pool[id(conn)] = conn
        return conn

    def dispose_connections(self) -> None:
        connections = self.pool.values()
        for conn in connections:
            conn.close()
        self.pool = {}

    def __repr__(self) -> str:
        return f"KDBEngine(pool_size: {len(self.pool)})"
