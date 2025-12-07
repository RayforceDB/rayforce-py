from __future__ import annotations

import platform
import typing as t

from rayforce.types import B8, F64, I16, I32, I64, Date, Symbol, Table, Timestamp, Vector

if t.TYPE_CHECKING:
    import polars as pl  # type: ignore[import-not-found]

    from rayforce.types.base import RayObject

if platform.system() == "Linux" and platform.machine() == "x86_64":
    print(
        "Warning: Use Polars plugin with caution.\n"
        "It is known to raise segmentation errors on x86_64 Linux machines"
    )


def _infer_ray_type_from_polars_dtype(dtype: t.Any) -> type[RayObject]:
    if hasattr(dtype, "__name__"):
        dtype_name = dtype.__name__.lower()
        if dtype_name in ("bool", "boolean"):
            return B8
        if dtype_name in ("i8", "int8", "i16", "int16"):
            return I16
        if dtype_name in ("i32", "int32"):
            return I32
        if dtype_name in ("i64", "int64", "int"):
            return I64
        if dtype_name in ("f32", "float32", "f64", "float64", "float"):
            return F64
        if dtype_name in ("str", "string", "object", "utf8"):
            return Symbol
        if dtype_name in ("datetime", "timestamp", "datetimes"):
            return Timestamp
        if dtype_name == "date":
            return Date

    dtype_type_name = type(dtype).__name__.lower()
    if dtype_type_name in ("datetime", "timestamp"):
        return Timestamp

    dtype_str = str(dtype).lower()
    if dtype_str in ("bool", "boolean"):
        return B8
    if dtype_str in ("i8", "int8", "i16", "int16"):
        return I16
    if dtype_str in ("i32", "int32"):
        return I32
    if dtype_str in ("i64", "int64", "int"):
        return I64
    if dtype_str in ("f32", "float32", "f64", "float64", "float"):
        return F64
    if dtype_str in ("str", "string", "object", "utf8"):
        return Symbol
    if dtype_str.startswith(("datetime", "timestamp")):
        return Timestamp
    if dtype_str == "date":
        return Date

    return Symbol


def from_polars(df: pl.DataFrame) -> Table:
    try:
        import polars as pl  # type: ignore[import-not-found]
    except ImportError as e:
        raise ImportError(
            "polars is required for from_polars(). Install it with: pip install rayforce-py[polars]"
        ) from e

    if not isinstance(df, pl.DataFrame):
        raise TypeError(f"Expected polars.DataFrame, got {type(df)}")

    if df.is_empty():
        raise ValueError("Cannot convert empty DataFrame")

    vectors: dict[str, Vector] = {}
    for col_name in df.columns:
        ray_type = _infer_ray_type_from_polars_dtype(df[col_name].dtype)
        vectors[col_name] = Vector(items=df[col_name].to_list(), ray_type=ray_type)

    return Table.from_dict(vectors)
