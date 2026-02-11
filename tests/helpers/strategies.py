"""Hypothesis strategies for property-based testing of rayforce types."""

from __future__ import annotations

import typing as t

from hypothesis import strategies as st

from rayforce import I64, Symbol, Table, Vector
from rayforce.types.scalars import F64


@st.composite
def vector_strategy(
    draw: st.DrawFn,
    ray_type: type = I64,
    min_size: int = 0,
    max_size: int = 50,
) -> Vector:
    """Generate a random Vector of the given type."""
    size = draw(st.integers(min_value=min_size, max_value=max_size))

    if ray_type is I64:
        items = draw(
            st.lists(
                st.integers(min_value=-(2**31), max_value=2**31 - 1), min_size=size, max_size=size
            )
        )
    elif ray_type is F64:
        items = draw(
            st.lists(
                st.floats(allow_nan=False, allow_infinity=False, min_value=-1e10, max_value=1e10),
                min_size=size,
                max_size=size,
            )
        )
    elif ray_type is Symbol:
        items = draw(
            st.lists(
                st.text(
                    min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("L", "N"))
                ),
                min_size=size,
                max_size=size,
            )
        )
    else:
        msg = f"Strategy not implemented for {ray_type}"
        raise NotImplementedError(msg)

    return Vector(items=items, ray_type=ray_type)


@st.composite
def table_strategy(
    draw: st.DrawFn,
    min_rows: int = 1,
    max_rows: int = 20,
    min_cols: int = 1,
    max_cols: int = 5,
) -> Table:
    """Generate a random Table with Symbol and I64 columns."""
    num_rows = draw(st.integers(min_value=min_rows, max_value=max_rows))
    num_cols = draw(st.integers(min_value=min_cols, max_value=max_cols))

    columns = {}
    for i in range(num_cols):
        col_name = f"col_{i}"
        if i == 0:
            # First column is always Symbol (common pattern)
            items = draw(
                st.lists(
                    st.text(
                        min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("L",))
                    ),
                    min_size=num_rows,
                    max_size=num_rows,
                )
            )
            columns[col_name] = Vector(items=items, ray_type=Symbol)
        else:
            items = draw(
                st.lists(
                    st.integers(min_value=-10000, max_value=10000),
                    min_size=num_rows,
                    max_size=num_rows,
                )
            )
            columns[col_name] = Vector(items=items, ray_type=I64)

    return Table(columns)
