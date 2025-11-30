"""
Python bindings for RayforceDB
"""
import os
import sys
import ctypes

version = "0.0.2"

if sys.platform == "linux":
    lib_name = "_rayforce_c.so"
    raykx_lib_name = "libraykx.so"
elif sys.platform == "darwin":
    lib_name = "_rayforce_c.so"
    raykx_lib_name = "libraykx.dylib"
elif sys.platform == "win32":
    lib_name = "rayforce.dll"
else:
    raise ImportError(f"Platform not supported: {sys.platform}")

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), lib_name)
raykx_lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins", raykx_lib_name)
if os.path.exists(lib_path) and os.path.exists(raykx_lib_path):
    try:
        ctypes.CDLL(lib_path, mode=ctypes.RTLD_GLOBAL)
        ctypes.CDLL(raykx_lib_path, mode=ctypes.RTLD_GLOBAL)
    except Exception as e:
        raise ImportError(f"Error loading CDLL: {e}")
else:
    raise ImportError(
        f"""
        Unable to load library - binaries are not compiled: \n
            - {lib_path} - Compiled: {os.path.exists(lib_path)}\n
            - {raykx_lib_path} - Compiled: {os.path.exists(raykx_lib_path)}\n
        Try to reinstall the library.
        """
    )


from .types import (  # noqa: E402
    F64,
    I16,
    I32,
    I64,
    U8,
    B8,
    C8,
    Symbol,
    QuotedSymbol,
    GUID,
    Date,
    Timestamp,
    Time,
    Vector,
    Dict,
    List,
    Table,
    String,
    RayInitException,
    TableColumnInterval,
)
from .plugins.raykx import KDBConnection, KDBEngine, ConnectionAlreadyClosed  # noqa: E402
from .io.ipc import IPCException, Connection, hopen  # noqa: E402

__all__ = [
    "F64",
    "I16",
    "I32",
    "I64",
    "U8",
    "B8",
    "C8",
    "Symbol",
    "QuotedSymbol",
    "GUID",
    "Date",
    "Timestamp",
    "Time",
    "Vector",
    "Dict",
    "List",
    "Table",
    "String",
    "RayInitException",
    "KDBConnection",
    "KDBEngine",
    "ConnectionAlreadyClosed",
    "IPCException",
    "Connection",
    "hopen",
    "TableColumnInterval",
]
