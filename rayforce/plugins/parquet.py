"""
Parquet Reading Implementation

For types I16, I32, I64, F64, B8, U8, TIMESTAMP, direct access to Arrow buffers is used.

Arrow string arrays have 3 buffers: null bitmap, offsets, data.
Create String object via `string_from_str(data + offset, length)`

Fallback - for unsupported types or on fast path - using `to_pylist()` to convert Arrow array to Python list (COW)
"""

from __future__ import annotations

import itertools
from pathlib import Path
import sys
import typing as t

from rayforce import _rayforce_c as r
from rayforce.ffi import FFI
from rayforce.plugins import errors
from rayforce.types import B8, F64, I16, I32, I64, U8, Date, String, Table, Time, Timestamp, Vector

if t.TYPE_CHECKING:
    from rayforce.types.base import RayObject

SUPPORTED_TYPES = (
    r.TYPE_I16,
    r.TYPE_I32,
    r.TYPE_I64,
    r.TYPE_F64,
    r.TYPE_B8,
    r.TYPE_U8,
    r.TYPE_TIMESTAMP,
    r.TYPE_C8,
)

print("Warning: parquet read is in beta and may behave unexpectedly")


class _Spinner:
    def __init__(self, enabled: bool, label: str = "Reading parquet"):
        self.enabled = enabled
        self.label = label
        self._cycle = itertools.cycle("|/-\\")
        self._last_len = 0

    def update(self, current: int, name: str, total: int) -> None:
        if not self.enabled:
            return

        msg = f"{self.label} {next(self._cycle)} . Column: {name} ({current} / {total})"
        pad = max(0, self._last_len - len(msg))
        sys.stdout.write("\r" + msg + (" " * pad))
        sys.stdout.flush()
        self._last_len = len(msg)

    def done(self) -> None:
        if not self.enabled:
            return
        sys.stdout.write("\r" + (" " * self._last_len) + "\r")
        sys.stdout.flush()


def _vector_from_pyarrow_buffer(arr: t.Any, ray_type: type[RayObject]) -> Vector:
    type_code = abs(ray_type.type_code)
    if type_code not in SUPPORTED_TYPES:
        raise errors.ParquetConversionError(f"Type code {type_code} is not supported")

    vector_ptr = FFI.init_vector_from_arrow_array(type_code=type_code, arrow_array=arr)
    return Vector(ptr=vector_ptr, ray_type=ray_type)


def load_parquet(path: str) -> Table:
    try:
        import pyarrow as pa  # type: ignore[import-not-found]
        from pyarrow import parquet as pq  # type: ignore[import-not-found]
    except ImportError as e:
        raise ImportError(
            "pyarrow is required for load_parquet(). Install it with: pip install pyarrow"
        ) from e

    _path = Path(path)
    _file: pa.Table = pq.read_table(_path.absolute())

    column_types: dict[str, type[RayObject]] = {}
    for field in _file.schema:
        if pa.types.is_boolean(field.type):
            column_types[field.name] = B8
        elif pa.types.is_uint8(field.type) or pa.types.is_int8(field.type):
            column_types[field.name] = U8
        elif pa.types.is_int16(field.type) or pa.types.is_uint16(field.type):
            column_types[field.name] = I16
        elif pa.types.is_int32(field.type) or pa.types.is_uint32(field.type):
            column_types[field.name] = I32
        elif pa.types.is_int64(field.type) or pa.types.is_uint64(field.type):
            column_types[field.name] = I64
        elif pa.types.is_float32(field.type) or pa.types.is_float64(field.type):
            column_types[field.name] = F64
        elif pa.types.is_string(field.type) or pa.types.is_large_string(field.type):
            column_types[field.name] = String
        elif pa.types.is_timestamp(field.type) or pa.types.is_date64(field.type):
            column_types[field.name] = Timestamp
        elif pa.types.is_date32(field.type):
            column_types[field.name] = Date
        elif pa.types.is_time32(field.type):
            column_types[field.name] = Time
        else:
            column_types[field.name] = String

    spinner = _Spinner(
        enabled=sys.stdout.isatty(),
        label=f"Reading {_path.absolute()} ({(_path.stat().st_size / (1024 * 1024)):.2f} MB)",
    )

    vectors: dict[str, Vector] = {}
    total = len(column_types)
    for i, col_name in enumerate(column_types, start=1):
        spinner.update(i, col_name, total)
        col = _file[col_name]
        arr = col.combine_chunks() if col.num_chunks > 1 else col.chunk(0)

        ray_type = column_types[col_name]
        try:
            vectors[col_name] = _vector_from_pyarrow_buffer(arr, ray_type)
        except Exception:
            values = arr.to_pylist()
            if ray_type == String:
                vectors[col_name] = Vector(items=[String(str(v)) for v in values], ray_type=String)
            else:
                vectors[col_name] = Vector(items=values, ray_type=ray_type)
        del arr

    spinner.done()
    del _file
    return Table(vectors)
