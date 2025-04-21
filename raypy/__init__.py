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

from .rayforce import *  # noqa: E402

__all__ = [
    "ray_init",
    "ray_clean",
    "ray_add",
    "ray_sub",
    "ray_mul",
    "ray_div",
    "ray_mod",
    "ray_fdiv",
    "ray_xbar",
    "ray_round",
    "ray_floor",
    "ray_sum",
    "ray_cnt",
    "ray_avg",
    "ray_min",
    "ray_max",
    "ray_ceil",
    "ray_med",
    "ray_dev",
    "vary_call",
    "ray_do",
    "ray_apply",
    "ray_gc",
    "ray_format",
    "ray_print",
    "ray_println",
    "ray_args",
    "ray_set_splayed",
    "ray_get_splayed",
    "ray_set_parted",
    "ray_get_parted",
    # Data types
    "i64",
    "i32",
    "i16",
    "u8",
    "b8",
    "f64",
    "symbol",
    "obj_t",
]
