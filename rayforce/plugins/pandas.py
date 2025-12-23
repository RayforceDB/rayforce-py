from __future__ import annotations

import datetime as dt
import typing as t

from rayforce.types import B8, F64, I16, I32, I64, Date, Symbol, Table, Timestamp, Vector

if t.TYPE_CHECKING:
    import pandas as pd  # type: ignore[import-untyped]

    from rayforce.types.base import RayObject


def _infer_ray_type_from_pandas_dtype(dtype: t.Any) -> type[RayObject]:
    dtype_str = str(dtype).lower()

    if dtype_str in ("bool", "boolean", "bool_", "bool8"):
        return B8

    if dtype_str in ("int8", "int16"):
        return I16
    if dtype_str in ("int32", "int"):
        return I32
    if dtype_str in ("int64", "int_", "long"):
        return I64
    if dtype_str in ("float32", "float", "float_", "float64", "double"):
        return F64
    if dtype_str in ("object", "string", "str", "str[pyarrow]", "str[python]"):
        return Symbol
    if dtype_str in ("datetime64[ns]", "datetime64", "datetime", "timestamp"):
        return Timestamp
    if dtype_str in ("date"):
        return Date

    if hasattr(dtype, "kind"):
        if dtype.kind == "b":
            return B8
        if dtype.kind == "i":
            return I64
        if dtype.kind == "f":
            return F64
        if dtype.kind == "O":
            return Symbol
        if dtype.kind == "M":
            return Timestamp

    return Symbol


def from_pandas(df: pd.DataFrame) -> Table:
    try:
        import pandas as pd  # type: ignore[import-untyped]
    except ImportError as e:
        raise ImportError(
            "pandas is required for from_pandas(). Install it with: pip install rayforce-py[pandas]"
        ) from e

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas.DataFrame, got {type(df)}")

    if df.empty:
        raise ValueError("Cannot convert empty DataFrame")

    vectors: dict[str, Vector] = {}
    for col_name in df.columns:
        col_series = df[col_name]
        dtype = col_series.dtype

        ray_type = _infer_ray_type_from_pandas_dtype(dtype)
        if dtype == "object" or str(dtype).lower() == "object":
            first_val = col_series.dropna().iloc[0] if not col_series.dropna().empty else None
            if first_val is not None:
                if isinstance(first_val, bool):
                    ray_type = B8
                elif isinstance(first_val, dt.date):
                    ray_type = Date
                elif isinstance(first_val, dt.datetime):
                    ray_type = Timestamp

        # Convert pandas Timestamp objects to datetime.datetime before passing to C API
        def convert_value(val):
            if pd.isna(val):
                return None
            # Convert pandas Timestamp to datetime.datetime
            if hasattr(val, "to_pydatetime"):
                return val.to_pydatetime()
            return val

        vectors[col_name] = Vector(
            items=[convert_value(val) for val in col_series.tolist()],
            ray_type=ray_type,
        )

    return Table.from_dict(vectors)
