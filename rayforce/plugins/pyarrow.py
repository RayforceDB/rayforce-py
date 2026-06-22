"""
PyArrow plugin.

Convert a ``pyarrow.Table`` into a Rayforce ``Table``, mirroring the
polars/pandas plugins. Numeric/boolean/string columns take a zero-copy
Arrow buffer fast path (see ``SUPPORTED_TYPES``); temporal and other types
fall back to ``to_pylist()``. The parquet plugin reuses this conversion.
"""

from __future__ import annotations

import typing as t

from rayforce import _rayforce_c as r
from rayforce.ffi import FFI
from rayforce.plugins import errors
from rayforce.types import (
    B8,
    F64,
    I16,
    I32,
    I64,
    U8,
    Date,
    String,
    Symbol,
    Table,
    Time,
    Timestamp,
    Vector,
)

if t.TYPE_CHECKING:
    import pyarrow as pa  # type: ignore[import-not-found]

    from rayforce.types.base import RayObject

# Types eligible for the zero-copy Arrow buffer fast path. Temporal types are
# deliberately excluded: their buffer carries an Arrow unit/epoch the fast path
# does not rescale, so they go through to_pylist() (like the polars/pandas
# plugins) to preserve correct values.
SUPPORTED_TYPES = (
    r.TYPE_I16,
    r.TYPE_I32,
    r.TYPE_I64,
    r.TYPE_F64,
    r.TYPE_B8,
    r.TYPE_U8,
    r.TYPE_STR,
)

_TEMPORAL_TYPES = (Date, Time, Timestamp)


def _infer_ray_type_from_arrow_type(pa: t.Any, arrow_type: t.Any) -> type[RayObject]:
    if pa.types.is_boolean(arrow_type):
        return B8
    if pa.types.is_uint8(arrow_type):
        return U8
    if (
        pa.types.is_int8(arrow_type)
        or pa.types.is_int16(arrow_type)
        or pa.types.is_uint16(arrow_type)
    ):
        # signed int8 widens to I16 (U8 is unsigned and would wrap negatives) — #M10
        return I16
    if pa.types.is_int32(arrow_type) or pa.types.is_uint32(arrow_type):
        return I32
    if pa.types.is_int64(arrow_type) or pa.types.is_uint64(arrow_type):
        return I64
    if pa.types.is_float32(arrow_type) or pa.types.is_float64(arrow_type):
        return F64
    if pa.types.is_string(arrow_type) or pa.types.is_large_string(arrow_type):
        return String
    if pa.types.is_timestamp(arrow_type) or pa.types.is_date64(arrow_type):
        return Timestamp
    if pa.types.is_date32(arrow_type):
        return Date
    if pa.types.is_time32(arrow_type):
        return Time
    return String


def _vector_from_arrow_buffer(arr: t.Any, ray_type: type[RayObject]) -> Vector:
    type_code = abs(ray_type.type_code)
    if type_code not in SUPPORTED_TYPES:
        raise errors.ParquetConversionError(f"Type code {type_code} is not supported")

    vector_ptr = FFI.init_vector_from_arrow_array(type_code=type_code, arrow_array=arr)
    return Vector(ptr=vector_ptr, ray_type=ray_type)


def _table_from_arrow(pa: t.Any, table: t.Any, *, strings_as_symbols: bool = False) -> Table:
    """Convert a ``pyarrow.Table`` to a Rayforce ``Table``. Handles zero-row
    tables (used by ``load_parquet`` for schema-only files). When
    ``strings_as_symbols`` is set, string columns become ``Symbol`` instead of
    ``String`` (matching the polars/pandas plugins)."""
    vectors: dict[str, Vector] = {}
    for field in table.schema:
        ray_type = _infer_ray_type_from_arrow_type(pa, field.type)
        col = table[field.name]
        arr = col.combine_chunks() if col.num_chunks > 1 else col.chunk(0)

        if ray_type is String and strings_as_symbols:
            vectors[field.name] = Vector(items=arr.to_pylist(), ray_type=Symbol)
            del arr
            continue

        if ray_type in _TEMPORAL_TYPES:
            vectors[field.name] = Vector(items=arr.to_pylist(), ray_type=ray_type)
            del arr
            continue

        try:
            vectors[field.name] = _vector_from_arrow_buffer(arr, ray_type)
        except Exception:
            values = arr.to_pylist()
            if ray_type == String:
                vectors[field.name] = Vector(
                    items=[String(str(v)) for v in values], ray_type=String
                )
            else:
                vectors[field.name] = Vector(items=values, ray_type=ray_type)
        del arr

    return Table(vectors)


def from_arrow(table: pa.Table, *, strings_as_symbols: bool = False) -> Table:
    try:
        import pyarrow as pa  # type: ignore[import-not-found]
    except ImportError as e:
        raise ImportError(
            "pyarrow is required for from_arrow(). Install it with: pip install rayforce-py[parquet]"
        ) from e

    if not isinstance(table, pa.Table):
        raise TypeError(f"Expected pyarrow.Table, got {type(table)}")

    if table.num_rows == 0:
        raise ValueError("Cannot convert empty Table")

    return _table_from_arrow(pa, table, strings_as_symbols=strings_as_symbols)
