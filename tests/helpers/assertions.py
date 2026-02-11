"""Custom assertion functions for rayforce test suite.

Usage::

    from tests.helpers.assertions import (
        assert_column_values,
        assert_columns,
        assert_contains_columns,
        assert_column_sorted,
        assert_row,
        assert_table_equal,
        assert_table_shape,
    )
"""

from __future__ import annotations

import typing as t

from rayforce.types import Table


# ---------------------------------------------------------------------------
# Table-level assertions
# ---------------------------------------------------------------------------


def assert_table_equal(
    left: Table,
    right: Table,
    *,
    check_order: bool = True,
    rtol: float = 1e-5,
) -> None:
    """Assert two Tables have identical structure and values."""
    left_cols = left.columns()
    right_cols = right.columns()
    assert left_cols == right_cols, f"Column mismatch:\n  left:  {left_cols}\n  right: {right_cols}"
    assert len(left) == len(right), f"Row count mismatch: left={len(left)}, right={len(right)}"
    left_vals = left.values()
    right_vals = right.values()
    for col_idx, col_name in enumerate(left_cols):
        for row_idx in range(len(left)):
            _assert_scalar_eq(
                left_vals[col_idx][row_idx].value,
                right_vals[col_idx][row_idx].value,
                label=f"[{col_name}][{row_idx}]",
                rtol=rtol,
            )


def assert_table_shape(table: Table, *, rows: int, cols: int) -> None:
    """Assert a table has the expected shape."""
    actual = table.shape()
    assert actual == (rows, cols), f"Shape mismatch: expected ({rows}, {cols}), got {actual}"


# ---------------------------------------------------------------------------
# Column-level assertions
# ---------------------------------------------------------------------------


def assert_columns(table: Table, expected: list[str]) -> None:
    """Assert column names match exactly (order-sensitive)."""
    actual = [str(c) for c in table.columns()]
    assert actual == expected, (
        f"Column names mismatch:\n  actual:   {actual}\n  expected: {expected}"
    )


def assert_contains_columns(table: Table, expected: list[str]) -> None:
    """Assert table contains at least these columns (order-insensitive)."""
    actual = {str(c) for c in table.columns()}
    missing = set(expected) - actual
    assert not missing, f"Missing columns: {missing}. Available: {actual}"


def assert_column_values(
    table: Table,
    column: str,
    expected: list,
    *,
    rtol: float = 1e-5,
) -> None:
    """Assert a column contains expected values in order."""
    actual = _extract_column(table, column)
    assert len(actual) == len(expected), (
        f"Column '{column}' length mismatch: got {len(actual)}, expected {len(expected)}"
    )
    for i, (a, e) in enumerate(zip(actual, expected)):
        _assert_scalar_eq(a, e, label=f"'{column}'[{i}]", rtol=rtol)


def assert_column_sorted(table: Table, column: str, *, desc: bool = False) -> None:
    """Assert a column is sorted in ascending (default) or descending order."""
    actual = _extract_column(table, column)
    for i in range(1, len(actual)):
        if desc:
            assert actual[i - 1] >= actual[i], (
                f"Column '{column}' not sorted desc at index {i}: {actual[i - 1]} < {actual[i]}"
            )
        else:
            assert actual[i - 1] <= actual[i], (
                f"Column '{column}' not sorted asc at index {i}: {actual[i - 1]} > {actual[i]}"
            )


def assert_column_set(table: Table, column: str, expected: set) -> None:
    """Assert a column contains exactly these values (order-insensitive)."""
    actual = set(_extract_column(table, column))
    assert actual == expected, (
        f"Column '{column}' set mismatch:\n  actual:   {actual}\n  expected: {expected}"
    )


# ---------------------------------------------------------------------------
# Row-level assertions
# ---------------------------------------------------------------------------


def assert_row(table: Table, idx: int, expected: dict[str, t.Any], *, rtol: float = 1e-5) -> None:
    """Assert a specific row matches expected values.

    Uses ``table.at_row(idx)`` and compares against *expected* dict.
    Only keys present in *expected* are checked (partial match).
    """
    row = table.at_row(idx)
    for col, exp_val in expected.items():
        actual_val = row[col]
        _assert_scalar_eq(actual_val, exp_val, label=f"row[{idx}]['{col}']", rtol=rtol)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _extract_column(table: Table, column: str) -> list:
    """Extract raw Python values from a table column."""
    cols = table.columns()
    col_list = [str(c) for c in cols] if not isinstance(cols, list) else cols
    assert column in col_list, f"Column '{column}' not found. Available: {col_list}"
    col_idx = col_list.index(column)
    vals = table.values()
    return [vals[col_idx][i].value for i in range(len(vals[col_idx]))]


def _assert_scalar_eq(actual: t.Any, expected: t.Any, *, label: str, rtol: float = 1e-5) -> None:
    """Compare two scalar values with float tolerance."""
    # Unwrap rayforce scalar objects to plain Python values
    if hasattr(actual, "value"):
        actual = actual.value
    if isinstance(actual, float) and isinstance(expected, (int, float)):
        expected_f = float(expected)
        assert abs(actual - expected_f) <= rtol * max(abs(actual), abs(expected_f), 1.0), (
            f"Value mismatch at {label}: {actual} != {expected_f} (rtol={rtol})"
        )
    else:
        assert actual == expected, f"Value mismatch at {label}: {actual!r} != {expected!r}"
