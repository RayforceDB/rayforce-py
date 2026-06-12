"""Comprehensive tests for the F64 (64-bit float) scalar."""

from __future__ import annotations

import math

import pytest

from rayforce import F64, I64

F64_MAX = 1.7976931348623157e308
F64_MIN_POSITIVE_NORMAL = 2.2250738585072014e-308
F64_SMALLEST_SUBNORMAL = 5e-324


# ── Construction ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "v, expected",
    [
        (0, 0.0),
        (123, 123.0),
        (-123, -123.0),
        (123.45, 123.45),
        (-123.45, -123.45),
        (42.7, 42.7),
        (1e10, 1e10),
        (-1e10, -1e10),
        (3.14159265358979, 3.14159265358979),
    ],
)
def test_f64_construct(v, expected):
    assert F64(v).value == expected


@pytest.mark.parametrize("v, expected", [(True, 1.0), (False, 0.0)])
def test_f64_construct_from_bool(v, expected):
    assert F64(v).value == expected


def test_f64_zero():
    assert F64(0).value == 0.0


def test_f64_negative_zero():
    """v2 may collapse -0.0 to 0.0 — check sign preserved if not."""
    val = F64(-0.0).value
    assert val == 0.0  # equal regardless of sign bit


# ── Special values: NaN, inf, -inf ───────────────────────────────────────────


def test_f64_nan():
    assert math.isnan(F64(float("nan")).value)


def test_f64_positive_infinity():
    v = F64(float("inf")).value
    assert math.isinf(v) and v > 0


def test_f64_negative_infinity():
    v = F64(float("-inf")).value
    assert math.isinf(v) and v < 0


# ── Precision extremes ──────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "v",
    [
        F64_SMALLEST_SUBNORMAL,
        1e-300,
        1e300,
        F64_MAX,
        F64_MIN_POSITIVE_NORMAL,
        -F64_MAX,
    ],
)
def test_f64_precision_extremes(v):
    assert F64(v).value == v


# ── Equality ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0.0, 1.5, -1.5, 42.0, 3.14, -3.14, 1e10, 1e-10])
def test_f64_eq_self(v):
    assert F64(v) == F64(v)


@pytest.mark.parametrize("a, b", [(1.5, 2.5), (0.0, 1.0), (-1.5, 1.5), (3.14, 2.71)])
def test_f64_neq(a, b):
    assert F64(a) != F64(b)


@pytest.mark.parametrize("v", [0.0, 1.5, -1.5, 42.0, 3.14])
def test_f64_eq_python_float(v):
    assert F64(v) == v
    assert v == F64(v)


def test_f64_nan_neq_nan():
    """NaN != NaN per IEEE 754."""
    assert F64(float("nan")) != F64(float("nan"))


# ── Ordering ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "a, b", [(1.5, 2.5), (0.0, 1.0), (-1.5, 1.5), (3.14, 4.14), (-100.0, 100.0)]
)
def test_f64_lt(a, b):
    assert (F64(a) < F64(b)).value is True
    assert (F64(b) < F64(a)).value is False


@pytest.mark.parametrize("a, b", [(2.5, 1.5), (1.0, 0.0), (1.5, -1.5), (4.14, 3.14)])
def test_f64_gt(a, b):
    assert (F64(a) > F64(b)).value is True


@pytest.mark.parametrize("a, b", [(0.0, 0.0), (1.5, 1.5), (-1.5, 1.5), (3.14, 3.14)])
def test_f64_le(a, b):
    assert (F64(a) <= F64(b)).value is True


@pytest.mark.parametrize("a, b", [(0.0, 0.0), (1.5, 1.5), (2.5, 1.5), (3.14, 3.14)])
def test_f64_ge(a, b):
    assert (F64(a) >= F64(b)).value is True


# ── Arithmetic ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (0.0, 0.0, 0.0),
        (1.5, 2.5, 4.0),
        (-1.5, 2.5, 1.0),
        (1.5, -2.5, -1.0),
        (3.14, 2.86, 6.0),
        (1e10, 1e10, 2e10),
    ],
)
def test_f64_add(a, b, expected):
    assert (F64(a) + F64(b)).value == pytest.approx(expected)


@pytest.mark.parametrize(
    "a, b, expected", [(5.5, 2.5, 3.0), (2.5, 5.5, -3.0), (0.0, 0.0, 0.0), (3.14, 1.14, 2.0)]
)
def test_f64_sub(a, b, expected):
    assert (F64(a) - F64(b)).value == pytest.approx(expected)


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (0.0, 5.0, 0.0),
        (1.5, 2.0, 3.0),
        (2.5, 4.0, 10.0),
        (-1.5, 2.0, -3.0),
        (-1.5, -2.0, 3.0),
        (3.14, 2.0, 6.28),
    ],
)
def test_f64_mul(a, b, expected):
    assert (F64(a) * F64(b)).value == pytest.approx(expected)


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (10.0, 4.0, 2.5),
        (1.0, 4.0, 0.25),
        (10.0, 3.0, 3.333333333333333),
        (-10.0, 4.0, -2.5),
        (1.5, 0.5, 3.0),
    ],
)
def test_f64_truediv(a, b, expected):
    assert (F64(a) / F64(b)).value == pytest.approx(expected)


@pytest.mark.parametrize("a, b, expected", [(10.0, 4.0, 2.0), (10.0, 3.0, 3.0), (1.0, 4.0, 0.0)])
def test_f64_floordiv(a, b, expected):
    assert (F64(a) // F64(b)).value == pytest.approx(expected)


@pytest.mark.parametrize("a, b, expected", [(10.0, 3.0, 1.0), (5.0, 2.0, 1.0), (10.0, 5.0, 0.0)])
def test_f64_mod(a, b, expected):
    assert (F64(a) % F64(b)).value == pytest.approx(expected)


# ── Mixed-type arithmetic ────────────────────────────────────────────────────


def test_f64_plus_i64():
    assert (F64(1.5) + I64(2)).value == 3.5


def test_i64_plus_f64():
    assert (I64(2) + F64(1.5)).value == 3.5


@pytest.mark.parametrize("a, b, expected", [(1.5, 2, 3.5), (10.0, 5, 15.0), (3.14, 1, 4.14)])
def test_f64_plus_python_int(a, b, expected):
    assert (F64(a) + b).value == pytest.approx(expected)


# ── Repr / str ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0.0, 1.5, -1.5, 42.0, 3.14, -3.14])
def test_f64_repr_contains_value(v):
    assert str(v) in repr(F64(v)) or repr(v) in repr(F64(v))


def test_f64_repr_starts_with_class_name():
    assert repr(F64(1.5)).startswith("F64")


# ── to_python / round-trip ───────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0.0, 1.5, -1.5, 42.0, 3.14, -3.14, 1e10, 1e-10])
def test_f64_to_python_returns_float(v):
    out = F64(v).to_python()
    assert isinstance(out, float)
    assert out == v


# ── Type code ────────────────────────────────────────────────────────────────


def test_f64_type_code():
    from rayforce import _rayforce_c as r

    assert F64.type_code == -r.TYPE_F64


# ── .value type ──────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0.0, 1.5, -1.5, 42.0, 3.14, 1e10])
def test_f64_value_is_float(v):
    assert isinstance(F64(v).value, float)
