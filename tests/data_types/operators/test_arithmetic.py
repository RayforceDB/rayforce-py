"""Comprehensive parametrized arithmetic tests across scalar/vector types."""

from __future__ import annotations

import pytest

from rayforce import F64, I16, I32, I64, Vector

# ── Scalar + scalar (same type) ──────────────────────────────────────────────


@pytest.mark.parametrize("ctor", [I16, I32, I64])
@pytest.mark.parametrize("a, b, expected", [(1, 2, 3), (5, 7, 12), (-1, 1, 0), (100, 200, 300)])
def test_int_add(ctor, a, b, expected):
    assert (ctor(a) + ctor(b)).value == expected


@pytest.mark.parametrize("ctor", [I16, I32, I64])
@pytest.mark.parametrize("a, b, expected", [(5, 3, 2), (10, 7, 3), (0, 5, -5), (100, 50, 50)])
def test_int_sub(ctor, a, b, expected):
    assert (ctor(a) - ctor(b)).value == expected


@pytest.mark.parametrize("ctor", [I16, I32, I64])
@pytest.mark.parametrize("a, b, expected", [(2, 3, 6), (5, 5, 25), (-2, 3, -6), (10, 0, 0)])
def test_int_mul(ctor, a, b, expected):
    assert (ctor(a) * ctor(b)).value == expected


@pytest.mark.parametrize("ctor", [I16, I32, I64])
@pytest.mark.parametrize(
    "a, b, expected", [(10, 4, 2.5), (20, 5, 4.0), (1, 4, 0.25), (-10, 4, -2.5)]
)
def test_int_truediv_returns_f64(ctor, a, b, expected):
    """v2 `/` is true division — returns F64 even on int operands."""
    result = ctor(a) / ctor(b)
    assert result.value == pytest.approx(expected)


@pytest.mark.parametrize("ctor", [I16, I32, I64])
@pytest.mark.parametrize("a, b, expected", [(10, 4, 2), (10, 3, 3), (1, 4, 0)])
def test_int_floordiv(ctor, a, b, expected):
    assert (ctor(a) // ctor(b)).value == expected


@pytest.mark.parametrize("ctor", [I16, I32, I64])
@pytest.mark.parametrize("a, b, expected", [(10, 3, 1), (5, 2, 1), (100, 7, 2)])
def test_int_mod(ctor, a, b, expected):
    assert (ctor(a) % ctor(b)).value == expected


# ── F64 ──────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "a, b, expected",
    [(1.5, 2.5, 4.0), (0.0, 0.0, 0.0), (-1.5, 1.5, 0.0), (100.0, 200.0, 300.0)],
)
def test_f64_add(a, b, expected):
    assert (F64(a) + F64(b)).value == pytest.approx(expected)


@pytest.mark.parametrize("a, b, expected", [(2.5, 4.0, 10.0), (1.5, 2.0, 3.0), (-1.5, 2.0, -3.0)])
def test_f64_mul(a, b, expected):
    assert (F64(a) * F64(b)).value == pytest.approx(expected)


# ── Cross-type: int + float promotes to float ───────────────────────────────


@pytest.mark.parametrize(
    "int_ctor",
    [I16, I32, I64],
)
@pytest.mark.parametrize("a, b, expected", [(1, 1.5, 2.5), (10, 0.5, 10.5), (-1, 2.5, 1.5)])
def test_int_plus_f64_returns_f64(int_ctor, a, b, expected):
    result = int_ctor(a) + F64(b)
    assert result.value == pytest.approx(expected)


# ── Vector arithmetic ───────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "items, addend, expected",
    [
        ([1, 2, 3], 1, [2, 3, 4]),
        ([10, 20, 30], 5, [15, 25, 35]),
        ([0, 0, 0], 100, [100, 100, 100]),
        ([-1, -2, -3], 10, [9, 8, 7]),
    ],
)
def test_vector_plus_scalar(items, addend, expected):
    v = Vector(items=items, ray_type=I64)
    result = v + addend
    assert [el.value for el in result] == expected


@pytest.mark.parametrize(
    "items, factor, expected",
    [
        ([1, 2, 3], 2, [2, 4, 6]),
        ([10, 20, 30], 3, [30, 60, 90]),
        ([1, 2, 3], 0, [0, 0, 0]),
        ([-1, -2, -3], -1, [1, 2, 3]),
    ],
)
def test_vector_times_scalar(items, factor, expected):
    v = Vector(items=items, ray_type=I64)
    result = v * factor
    assert [el.value for el in result] == expected


@pytest.mark.parametrize(
    "items, sub, expected",
    [
        ([10, 20, 30], 5, [5, 15, 25]),
        ([0, 0, 0], 1, [-1, -1, -1]),
        ([100, 200, 300], 100, [0, 100, 200]),
    ],
)
def test_vector_minus_scalar(items, sub, expected):
    v = Vector(items=items, ray_type=I64)
    result = v - sub
    assert [el.value for el in result] == expected


@pytest.mark.parametrize(
    "items, divisor, expected",
    [
        ([10, 20, 30], 5, [2.0, 4.0, 6.0]),
        ([1, 2, 3], 2, [0.5, 1.0, 1.5]),
        ([100, 200, 300], 4, [25.0, 50.0, 75.0]),
    ],
)
def test_vector_truediv_scalar(items, divisor, expected):
    """v2 `/` on int vector returns F64 vector."""
    v = Vector(items=items, ray_type=I64)
    result = v / divisor
    assert [el.value for el in result] == pytest.approx(expected)


@pytest.mark.parametrize(
    "items, divisor, expected",
    [
        ([10, 20, 30], 5, [2, 4, 6]),
        ([1, 2, 3], 2, [0, 1, 1]),
        ([100, 200, 300], 7, [14, 28, 42]),
    ],
)
def test_vector_floordiv_scalar(items, divisor, expected):
    v = Vector(items=items, ray_type=I64)
    result = v // divisor
    assert [el.value for el in result] == expected


# ── Vector + Vector ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "a, b, expected",
    [
        ([1, 2, 3], [4, 5, 6], [5, 7, 9]),
        ([10, 20, 30], [1, 2, 3], [11, 22, 33]),
        ([0, 0, 0], [1, 2, 3], [1, 2, 3]),
    ],
)
def test_vector_plus_vector(a, b, expected):
    va = Vector(items=a, ray_type=I64)
    vb = Vector(items=b, ray_type=I64)
    result = va + vb
    assert [el.value for el in result] == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        ([10, 20, 30], [1, 2, 3], [9, 18, 27]),
        ([5, 5, 5], [1, 2, 3], [4, 3, 2]),
    ],
)
def test_vector_minus_vector(a, b, expected):
    va = Vector(items=a, ray_type=I64)
    vb = Vector(items=b, ray_type=I64)
    result = va - vb
    assert [el.value for el in result] == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        ([2, 3, 4], [3, 4, 5], [6, 12, 20]),
        ([1, 2, 3], [10, 10, 10], [10, 20, 30]),
    ],
)
def test_vector_times_vector(a, b, expected):
    va = Vector(items=a, ray_type=I64)
    vb = Vector(items=b, ray_type=I64)
    result = va * vb
    assert [el.value for el in result] == expected
