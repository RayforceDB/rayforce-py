import os
import ctypes
from pathlib import Path

package_dir = Path(__file__).resolve().parent
os.environ["DYLD_LIBRARY_PATH"] = (
    str(package_dir) + ":" + os.environ.get("DYLD_LIBRARY_PATH", "")
)

# Pre-load the dylib from the same directory as the package
try:
    dylib_path = os.path.join(package_dir, "librayforce.dylib")
    if os.path.exists(dylib_path):
        ctypes.CDLL(dylib_path)
except Exception as e:
    print(f"Warning: Could not pre-load librayforce.dylib: {e}")

from .obj import (  # noqa: E402
    # Main atomic object
    RayforceObject,
)
from .misc import (  # noqa: E402
    initialize,
)
from .types import (  # noqa: E402
    # Rayforce data types
    b8,
    i16,
    i32,
    i64,
    f64,
)
from .operations import (  # noqa: E402
    # Mathematical operations
    add,
    sub,
    mul,
    div,
    fdiv,
)

# Initialize runtime
initialize()

__all__ = [
    "RayforceObject",
    "b8",
    "i16",
    "i32",
    "i64",
    "f64",
    "add",
    "sub",
    "mul",
    "div",
    "fdiv",
    "initialize",
]
