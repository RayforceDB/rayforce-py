"""
Raypy - Python bindings for Rayforce library
"""

import os
import sys
import ctypes

# Get the correct library name based on the OS
if sys.platform == "darwin":
    lib_name = "librayforce.dylib"
    raykx_lib_name = "libraykx.dylib"
elif sys.platform == "win32":
    lib_name = "rayforce.dll"
else:  # Linux and other Unix-like
    lib_name = "_rayforce.so"
    raykx_lib_name = "libraykx.so"

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), lib_name)
if os.path.exists(lib_path):
    try:
        ctypes.CDLL(lib_path, mode=ctypes.RTLD_GLOBAL)
    except Exception as e:
        print(f"Error loading library: {e}")


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
