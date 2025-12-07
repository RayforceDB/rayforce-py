from datetime import UTC, datetime
from pathlib import Path
import sys

from rayforce import _rayforce_c as r
from rayforce import utils
from rayforce.core import FFI
from rayforce.plugins import exceptions

if sys.platform == "darwin":
    raykx_lib_name = "libraykx.dylib"
elif sys.platform == "win32":
    raykx_lib_name = "libraykx.dll"
else:
    raykx_lib_name = "libraykx.so"

# Construct the path to the lib file relative to this directory
c_plugin_compiled_path = str(Path(__file__).resolve().parent / raykx_lib_name)


# (.kx.hopen "127.0.0.1:5101")
_fn_hopen = FFI.loadfn_from_file(
    filename=c_plugin_compiled_path,
    fn_name="raykx_hopen",
    args_count=1,
)
# (.kx.hclose h)
_fn_hclose = FFI.loadfn_from_file(
    filename=c_plugin_compiled_path,
    fn_name="raykx_hclose",
    args_count=1,
)
# (.kx.send h "1+2")
_fn_send = FFI.loadfn_from_file(
    filename=c_plugin_compiled_path,
    fn_name="raykx_send",
    args_count=2,
)


class KDBConnection:
    ptr: r.RayObject
    _type = -r.TYPE_I64  # Descriptor

    def __init__(
        self,
        engine: KDBEngine,
        conn: r.RayObject,
    ) -> None:
        if (_type := conn.get_obj_type()) != self._type:
            raise ValueError(
                f"Invalid KDB connection object type. Expected {self._type}, got {_type}",
            )

        self.engine = engine
        self.ptr = conn
        self.established_at = datetime.now(UTC)
        self.disposed_at: datetime | None = None
        self.is_closed = False

    def __execute_kdb_query(self, query: str) -> r.RayObject:
        obj = FFI.init_list()
        FFI.push_obj(obj, _fn_send)
        FFI.push_obj(obj, self.ptr)
        FFI.push_obj(obj, FFI.init_string(query))
        return FFI.eval_obj(obj)

    def __close_kdb_connection(self) -> None:
        obj = FFI.init_list()
        FFI.push_obj(obj, _fn_hclose)
        FFI.push_obj(obj, self.ptr)
        FFI.eval_obj(obj)

    def execute(self, query: str) -> r.RayObject:
        if self.is_closed:
            raise exceptions.KDBConnectionAlreadyClosedError

        result = self.__execute_kdb_query(query=query)
        if result.get_obj_type() == r.TYPE_ERR:
            error_message = FFI.get_error_message(result)
            if error_message and error_message.startswith("'ipc_send"):
                raise exceptions.KDBConnectionAlreadyClosedError

            raise ValueError(f"Failed to execute statement: {error_message}")

        return utils.ray_to_python(result)

    def close(self) -> None:
        self.__close_kdb_connection()
        self.is_closed = True
        self.disposed_at = datetime.now(UTC)

    def __enter__(self) -> KDBConnection:
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.close()

    def __repr__(self) -> str:
        if self.is_closed:
            return f"KDBConnection(id:{id(self)}) - disposed at {self.disposed_at.isoformat() if self.disposed_at else 'Unknown'}"
        return f"KDBConnection(id:{id(self)}) - established at {self.established_at.isoformat()}"


class KDBEngine:
    def __init__(self, host: str, port: int | None = None) -> None:
        self.url = f"{host}:{port}" if port is not None else host
        self.pool: dict[int, KDBConnection] = {}

    def __open_kdb_connection(self) -> r.RayObject:
        host = FFI.init_string(self.url)
        obj = FFI.init_list()
        FFI.push_obj(obj, _fn_hopen)
        FFI.push_obj(obj, host)
        return FFI.eval_obj(obj)

    def acquire(self) -> KDBConnection:
        _conn = self.__open_kdb_connection()
        if _conn.get_obj_type() == r.TYPE_ERR:
            raise ValueError(f"Error when establishing connection: {FFI.get_error_message(_conn)}")

        conn = KDBConnection(engine=self, conn=_conn)
        self.pool[id(conn)] = conn
        return conn

    def dispose_connections(self) -> None:
        connections = self.pool.values()
        for conn in connections:
            conn.close()
        self.pool = {}

    def __repr__(self) -> str:
        return f"KDBEngine(pool_size: {len(self.pool)})"
