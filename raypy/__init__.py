"""
Raypy - Python bindings for Rayforce library
"""

import os
import ctypes
import sys

__version__ = '0.1.0'

# Загружаем библиотеку librayforce.dylib прежде, чем импортировать модуль _rayforce
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'librayforce.dylib')
if os.path.exists(lib_path):
    # Используем RTLD_GLOBAL, чтобы символы были доступны для других модулей
    try:
        _lib = ctypes.CDLL(lib_path, mode=ctypes.RTLD_GLOBAL)
    except Exception as e:
        print(f"Error loading library: {e}")

# Создаем каталог types, если его нет
types_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'types')
if not os.path.exists(types_dir):
    os.makedirs(types_dir)
    # Создаем пустой __init__.py в каталоге types
    with open(os.path.join(types_dir, '__init__.py'), 'w') as f:
        f.write('# Types package\n')

