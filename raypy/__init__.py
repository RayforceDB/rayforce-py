import os
import platform
import ctypes
from pathlib import Path

package_dir = Path(__file__).resolve().parent

# Set appropriate library path environment variable based on platform
system = platform.system()
if system == "Darwin":
    os.environ["DYLD_LIBRARY_PATH"] = (
        str(package_dir) + ":" + os.environ.get("DYLD_LIBRARY_PATH", "")
    )

    # Pre-load the dylib from the same directory as the package
    try:
        lib_path = os.path.join(package_dir, "librayforce.dylib")
        if os.path.exists(lib_path):
            ctypes.CDLL(lib_path)
    except Exception as e:
        print(f"Warning: Could not pre-load librayforce.dylib: {e}")

elif system == "Linux":
    # For Linux, we need to directly load the library with RTLD_GLOBAL
    # before other imports to make symbols available
    try:
        # Update library path
        os.environ["LD_LIBRARY_PATH"] = (
            str(package_dir) + ":" + os.environ.get("LD_LIBRARY_PATH", "")
        )

        # Load the library directly from its absolute path with RTLD_GLOBAL
        # This is the most reliable way to make symbols available
        lib_path = os.path.join(package_dir, "librayforce.so")
        if os.path.exists(lib_path):
            # Use absolute path and RTLD_GLOBAL
            ctypes.CDLL(lib_path, mode=ctypes.RTLD_GLOBAL)
        else:
            raise FileNotFoundError(f"Shared library not found at {lib_path}")
    except Exception as e:
        print(f"Warning: Could not pre-load librayforce.so: {e}")

# Only import after the library has been loaded
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
from .math_operations import (  # noqa: E402
    # Mathematical operations
    add,
    sub,
    mul,
    div,
    fdiv,
    mod,
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
    "mod",
    "initialize",
]
