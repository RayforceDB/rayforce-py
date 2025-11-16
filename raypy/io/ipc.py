from raypy import _rayforce as r
from raypy.core.ffi import FFI


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

    def execute(self, data: str) -> None:
        if self._closed:
            raise IPCException("Cannot write to closed connection")

        FFI.write(self.handle, FFI.init_string(data))

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
            except:
                pass


def hopen(host: str, port: int) -> Connection:
    return Connection(FFI.hopen(host, port))
