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


_POLARS_DTYPE_TO_RAY: dict[str, type[RayObject]] = {
    "bool": B8,
    "boolean": B8,
    "i8": I16,
    "int8": I16,
    "i16": I16,
    "int16": I16,
    "i32": I32,
    "int32": I32,
    "i64": I64,
    "int64": I64,
    "int": I64,
    "f32": F64,
    "float32": F64,
    "f64": F64,
    "float64": F64,
    "float": F64,
    "str": Symbol,
    "string": Symbol,
    "object": Symbol,
    "utf8": Symbol,
    "datetime": Timestamp,
    "timestamp": Timestamp,
    "datetimes": Timestamp,
    "date": Date,
}


def _infer_ray_type_from_polars_dtype(dtype: t.Any) -> type[RayObject]:
    # Polars dtypes carry their canonical name via `__name__`; the type itself
    # (a metaclass instance) also has a useful `__name__`. Fall back to
    # str(dtype) for "Datetime(...)" / "Timestamp(...)" parametric forms.
    candidates: list[str] = []
    if hasattr(dtype, "__name__"):
        candidates.append(dtype.__name__.lower())
    candidates.append(type(dtype).__name__.lower())
    candidates.append(str(dtype).lower())

    for name in candidates:
        ray_type = _POLARS_DTYPE_TO_RAY.get(name)
        if ray_type is not None:
            return ray_type
        if name.startswith(("datetime", "timestamp")):
            return Timestamp
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

    return Table(vectors)
