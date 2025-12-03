from typing import Any
from rayforce.types.containers.vector import String
from rayforce.utils import ray_to_python
from rayforce import _rayforce_c as r
from rayforce.core.ffi import FFI


class IPCException(Exception): ...


class Connection:
    """
    Connection to a remote RayforceDB process
    """

    def __init__(self, handle: r.RayObject) -> None:
        """
        Initialize connection with a handle.
        """
        self.handle = handle
        self._closed = False

    def execute(self, data: Any) -> Any:
        if self._closed:
            raise IPCException("Cannot write to closed connection")

        if isinstance(data, str):
            result = FFI.write(self.handle, FFI.init_string(data))
        elif hasattr(data, "ptr"):
            result = FFI.write(self.handle, data.ptr)
        elif hasattr(data, "ipc"):
            result = FFI.write(self.handle, data.ipc)
        else:
            raise IPCException(f"Unsupported IPC data to send: {type(data)}")

        return ray_to_python(result)

    def close(self) -> None:
        if not self._closed:
            FFI.hclose(self.handle)
            self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __del__(self) -> None:
        if not self._closed:
            try:
                self.close()
            except Exception:
                pass


def hopen(host: str, port: int) -> Connection:
    path = String(f"{host}:{port}")
    return Connection(FFI.hopen(path.ptr))
