"""Comprehensive comparison operator tests across scalar/vector types."""

from __future__ import annotations

import pytest

from rayforce import I16, I32, I64, Vector

# ── Scalar comparisons ──────────────────────────────────────────────────────


@pytest.mark.parametrize("ctor", [I16, I32, I64])
@pytest.mark.parametrize("a, b", [(0, 0), (1, 1), (-1, -1), (42, 42), (100, 100), (1000, 1000)])
def test_scalar_eq_self(ctor, a, b):
    assert ctor(a) == ctor(b)


@pytest.mark.parametrize("ctor", [I16, I32, I64])
@pytest.mark.parametrize("a, b", [(0, 1), (1, 2), (-1, 0), (42, 100), (1000, 999)])
def test_scalar_neq(ctor, a, b):
    assert ctor(a) != ctor(b)


@pytest.mark.parametrize("ctor", [I16, I32, I64])
@pytest.mark.parametrize("a, b", [(0, 1), (-1, 0), (1, 2), (-100, 100), (42, 100)])
def test_scalar_lt(ctor, a, b):
    assert (ctor(a) < ctor(b)).value is True


@pytest.mark.parametrize("ctor", [I16, I32, I64])
@pytest.mark.parametrize("a, b", [(1, 0), (0, -1), (100, -100), (100, 42)])
def test_scalar_gt(ctor, a, b):
    assert (ctor(a) > ctor(b)).value is True


# ── Vector comparisons (element-wise → bool vector) ────────────────────────


@pytest.mark.parametrize(
    "items, scalar, expected",
    [
        ([1, 2, 3], 2, [False, False, True]),
        ([10, 20, 30], 15, [False, True, True]),
        ([1, 2, 3], 0, [True, True, True]),
        ([1, 2, 3], 100, [False, False, False]),
    ],
)
def test_vector_gt_scalar(items, scalar, expected):
    v = Vector(items=items, ray_type=I64)
    result = v > scalar
    assert [el.value for el in result] == expected


@pytest.mark.parametrize(
    "items, scalar, expected",
    [
        ([1, 2, 3], 2, [True, False, False]),
        ([10, 20, 30], 15, [True, False, False]),
        ([1, 2, 3], 100, [True, True, True]),
        ([1, 2, 3], 0, [False, False, False]),
    ],
)
def test_vector_lt_scalar(items, scalar, expected):
    v = Vector(items=items, ray_type=I64)
    result = v < scalar
    assert [el.value for el in result] == expected


@pytest.mark.parametrize(
    "items, scalar, expected_lt, expected_gt",
    [
        ([1, 2, 3], 2, [True, False, False], [False, False, True]),
        ([10, 20, 30], 20, [True, False, False], [False, False, True]),
    ],
)
def test_vector_lt_gt_consistency(items, scalar, expected_lt, expected_gt):
    """Vector < scalar and Vector > scalar are mutually exclusive (modulo equal)."""
    v = Vector(items=items, ray_type=I64)
    lt = [el.value for el in (v < scalar)]
    gt = [el.value for el in (v > scalar)]
    assert lt == expected_lt
    assert gt == expected_gt


@pytest.mark.parametrize(
    "items, scalar, expected",
    [
        ([1, 2, 3], 2, [True, True, False]),
        ([10, 20, 30], 20, [True, True, False]),
        ([1, 2, 3], 0, [False, False, False]),
    ],
)
def test_vector_le_scalar(items, scalar, expected):
    v = Vector(items=items, ray_type=I64)
    result = v <= scalar
    assert [el.value for el in result] == expected


@pytest.mark.parametrize(
    "items, scalar, expected",
    [
        ([1, 2, 3], 2, [False, True, True]),
        ([10, 20, 30], 20, [False, True, True]),
        ([1, 2, 3], 100, [False, False, False]),
    ],
)
def test_vector_ge_scalar(items, scalar, expected):
    v = Vector(items=items, ray_type=I64)
    result = v >= scalar
    assert [el.value for el in result] == expected


# ── Vector vs vector (whole-Python equality) ───────────────────────────────


@pytest.mark.parametrize(
    "a, b",
    [
        ([1, 2, 3], [1, 2, 3]),
        ([], []),
        ([42], [42]),
        ([10, 20], [10, 20]),
    ],
)
def test_vector_whole_eq_true(a, b):
    va = Vector(items=a, ray_type=I64)
    vb = Vector(items=b, ray_type=I64)
    assert (va == vb) is True


@pytest.mark.parametrize(
    "a, b",
    [
        ([1, 2, 3], [4, 5, 6]),
        ([1, 2], [1, 2, 3]),
        ([0], [1]),
        ([10, 20], [20, 10]),
    ],
)
def test_vector_whole_eq_false(a, b):
    va = Vector(items=a, ray_type=I64)
    vb = Vector(items=b, ray_type=I64)
    assert (va == vb) is False
