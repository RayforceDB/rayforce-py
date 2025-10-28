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

# Expose fluent/Pythonic API
from raypy.types.fluent import Table, Column, Expression, lookup

__all__ = ['Table', 'Column', 'Expression', 'lookup']
