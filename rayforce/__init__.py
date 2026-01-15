"""
Python bindings for RayforceDB
"""

import ctypes
from pathlib import Path
import sys

from rayforce.ffi import FFI

FFI.init_runtime()

version = "0.5.1"

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

lib_path = Path(__file__).resolve().parent / lib_name
raykx_lib_path = Path(__file__).resolve().parent / "plugins" / raykx_lib_name
if lib_path.exists() and raykx_lib_path.exists():
    try:
        ctypes.CDLL(str(lib_path), mode=ctypes.RTLD_GLOBAL)
        ctypes.CDLL(str(raykx_lib_path), mode=ctypes.RTLD_GLOBAL)
    except Exception as e:
        raise ImportError(f"Error loading CDLL: {e}") from e
else:
    raise ImportError(
        f"""
        Unable to load library - binaries are not compiled: \n
            - {lib_path} - Compiled: {lib_path.exists()}\n
            - {raykx_lib_path} - Compiled: {raykx_lib_path.exists()}\n
        Try to reinstall the library.
        """,
    )


from .errors import (  # noqa: E402
    RayforceArityError,
    RayforceConversionError,
    RayforceDomainError,
    RayforceError,
    RayforceEvaluationError,
    RayforceIndexError,
    RayforceInitError,
    RayforceLengthError,
    RayforceNYIError,
    RayforceOkError,
    RayforceOSError,
    RayforceParseError,
    RayforcePartedTableError,
    RayforceQueryCompilationError,
    RayforceTCPError,
    RayforceThreadError,
    RayforceTypeError,
    RayforceTypeRegistryError,
    RayforceUserError,
    RayforceValueError,
)
from .network import (  # noqa: E402
    TCPClient,
    TCPServer,
)
from .types import (  # noqa: E402
    B8,
    C8,
    F64,
    GUID,
    I16,
    I32,
    I64,
    U8,
    Column,
    Date,
    Dict,
    Expression,
    Fn,
    List,
    Null,
    Operation,
    QuotedSymbol,
    String,
    Symbol,
    Table,
    TableColumnInterval,
    Time,
    Timestamp,
    Vector,
)
from .utils import (  # noqa: E402
    eval_obj,
    eval_str,
    python_to_ray,
    ray_to_python,
)

core_version = String(eval_str("(sysinfo)")["hash"]).to_python()

__all__ = [
    "B8",
    "C8",
    "F64",
    "GUID",
    "I16",
    "I32",
    "I64",
    "U8",
    "Column",
    "Date",
    "Dict",
    "Expression",
    "Fn",
    "List",
    "Null",
    "Operation",
    "QuotedSymbol",
    "RayforceArityError",
    "RayforceConversionError",
    "RayforceDomainError",
    "RayforceError",
    "RayforceEvaluationError",
    "RayforceIndexError",
    "RayforceInitError",
    "RayforceInitError",
    "RayforceLengthError",
    "RayforceNYIError",
    "RayforceOSError",
    "RayforceOkError",
    "RayforceParseError",
    "RayforcePartedTableError",
    "RayforceQueryCompilationError",
    "RayforceTCPError",
    "RayforceThreadError",
    "RayforceTypeError",
    "RayforceTypeRegistryError",
    "RayforceUserError",
    "RayforceValueError",
    "String",
    "Symbol",
    "TCPClient",
    "TCPServer",
    "Table",
    "TableColumnInterval",
    "Time",
    "Timestamp",
    "Vector",
    "core_version",
    "eval_obj",
    "eval_str",
    "python_to_ray",
    "ray_to_python",
    "version",
]
