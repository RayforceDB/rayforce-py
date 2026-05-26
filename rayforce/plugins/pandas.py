from __future__ import annotations

import datetime as dt
import typing as t

from rayforce.types import B8, F64, I16, I32, I64, Date, Symbol, Table, Timestamp, Vector

if t.TYPE_CHECKING:
    import pandas as pd  # type: ignore[import-untyped]

    from rayforce.types.base import RayObject


_PANDAS_DTYPE_TO_RAY: dict[str, type[RayObject]] = {
    "bool": B8,
    "boolean": B8,
    "bool_": B8,
    "bool8": B8,
    "int8": I16,
    "int16": I16,
    "int32": I32,
    "int": I32,
    "int64": I64,
    "int_": I64,
    "long": I64,
    "float32": F64,
    "float": F64,
    "float_": F64,
    "float64": F64,
    "double": F64,
    "object": Symbol,
    "string": Symbol,
    "str": Symbol,
    "str[pyarrow]": Symbol,
    "str[python]": Symbol,
    "datetime64[ns]": Timestamp,
    "datetime64": Timestamp,
    "datetime": Timestamp,
    "timestamp": Timestamp,
    "date": Date,
}

# numpy dtype.kind → ray type, used when string lookup fails.
_PANDAS_DTYPE_KIND_TO_RAY: dict[str, type[RayObject]] = {
    "b": B8,
    "i": I64,
    "f": F64,
    "O": Symbol,
    "M": Timestamp,
}


def _infer_ray_type_from_pandas_dtype(dtype: t.Any) -> type[RayObject]:
    ray_type = _PANDAS_DTYPE_TO_RAY.get(str(dtype).lower())
    if ray_type is not None:
        return ray_type
    kind = getattr(dtype, "kind", None)
    if kind is not None:
        ray_type = _PANDAS_DTYPE_KIND_TO_RAY.get(kind)
        if ray_type is not None:
            return ray_type
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

    return Table(vectors)
