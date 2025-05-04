"""
Raypy - Python bindings for Rayforce library
"""

import os
import ctypes

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "librayforce.dylib")
if os.path.exists(lib_path):
    try:
        ctypes.CDLL(lib_path, mode=ctypes.RTLD_GLOBAL)
    except Exception as e:
        print(f"Error loading library: {e}")
