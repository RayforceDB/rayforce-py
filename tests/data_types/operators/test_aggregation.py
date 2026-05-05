"""Comprehensive aggregation operator tests."""

from __future__ import annotations

import pytest

from rayforce import F64, I64, Vector

# ── sum / count / first / last ─────────────────────────────────────────────


@pytest.mark.parametrize(
    "items, expected_sum",
    [
        ([1], 1),
        ([1, 2, 3], 6),
        ([1, 2, 3, 4, 5], 15),
        ([10, 20, 30], 60),
        (list(range(100)), 4950),
        ([-1, -2, -3], -6),
        ([0, 0, 0], 0),
    ],
)
def test_vector_sum(items, expected_sum):
    v = Vector(items=items, ray_type=I64)
    assert v.sum() == expected_sum


@pytest.mark.parametrize(
    "items, expected",
    [
        ([1], 1),
        ([1, 2, 3], 3),
        (list(range(10)), 10),
        (list(range(100)), 100),
    ],
)
def test_vector_len(items, expected):
    v = Vector(items=items, ray_type=I64)
    assert len(v) == expected


@pytest.mark.parametrize(
    "items, expected_first",
    [([1, 2, 3], 1), ([100, 200, 300], 100), ([-5, 10, 20], -5), ([42], 42)],
)
def test_vector_first(items, expected_first):
    v = Vector(items=items, ray_type=I64)
    assert v.first() == expected_first


@pytest.mark.parametrize(
    "items, expected_last",
    [([1, 2, 3], 3), ([100, 200, 300], 300), ([10, 20, -5], -5), ([42], 42)],
)
def test_vector_last(items, expected_last):
    v = Vector(items=items, ray_type=I64)
    assert v.last() == expected_last


# ── min / max ────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "items, expected",
    [
        ([3, 1, 4, 1, 5], 1),
        ([10, 20, 30], 10),
        ([-5, -10, -1], -10),
        ([100], 100),
        ([1, 2, 3, 4, 5], 1),
    ],
)
def test_vector_min(items, expected):
    v = Vector(items=items, ray_type=I64)
    assert v.min() == expected


@pytest.mark.parametrize(
    "items, expected",
    [
        ([3, 1, 4, 1, 5], 5),
        ([10, 20, 30], 30),
        ([-5, -10, -1], -1),
        ([100], 100),
        ([1, 2, 3, 4, 5], 5),
    ],
)
def test_vector_max(items, expected):
    v = Vector(items=items, ray_type=I64)
    assert v.max() == expected


# ── average / mean ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "items, expected_avg",
    [
        ([1, 2, 3], 2.0),
        ([1, 2, 3, 4, 5], 3.0),
        ([10, 20, 30], 20.0),
        ([100, 200], 150.0),
        ([0, 0, 0], 0.0),
    ],
)
def test_vector_average(items, expected_avg):
    v = Vector(items=items, ray_type=I64)
    assert v.average() == pytest.approx(expected_avg)


# ── F64 aggregations ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "items, expected", [([1.5, 2.5, 3.5], 7.5), ([0.5, 0.5, 0.5], 1.5), ([10.0, 20.0], 30.0)]
)
def test_vector_sum_f64(items, expected):
    v = Vector(items=items, ray_type=F64)
    assert v.sum() == pytest.approx(expected)


@pytest.mark.parametrize("items, expected_avg", [([1.0, 2.0, 3.0], 2.0), ([10.0, 20.0], 15.0)])
def test_vector_average_f64(items, expected_avg):
    v = Vector(items=items, ray_type=F64)
    assert v.average() == pytest.approx(expected_avg)


# ── Vector reverse ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "items, expected",
    [
        ([1, 2, 3], [3, 2, 1]),
        ([10, 20, 30, 40], [40, 30, 20, 10]),
        ([-1, -2, -3], [-3, -2, -1]),
        ([42], [42]),
    ],
)
def test_vector_reverse(items, expected):
    v = Vector(items=items, ray_type=I64)
    result = v.reverse()
    assert [el.value for el in result] == expected
