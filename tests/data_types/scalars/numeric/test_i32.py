"""Comprehensive tests for the I32 (signed 32-bit integer) scalar."""

from __future__ import annotations

import pytest

from rayforce import I32, errors

I32_MAX = 2**31 - 1
I32_MIN = -(2**31)  # null sentinel (0Ni)


# ── Construction ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "v",
    [0, 1, -1, 42, -42, 100, 1000, 1_000_000, -1_000_000, 2**20, -(2**20), 2**30, -(2**30)],
)
def test_i32_construct_from_int(v):
    assert I32(v).value == v


@pytest.mark.parametrize("v, expected", [(True, 1), (False, 0)])
def test_i32_construct_from_bool(v, expected):
    assert I32(v).value == expected


def test_i32_zero():
    assert I32(0).value == 0


def test_i32_max_value():
    assert I32(I32_MAX).value == I32_MAX


def test_i32_min_is_null_sentinel():
    """I32_MIN is the v2 null sentinel."""
    assert I32(I32_MIN).value is None


@pytest.mark.parametrize(
    "v, expected",
    [
        (I32_MAX + 1, None),  # MAX+1 wraps to MIN (null)
        (I32_MIN - 1, I32_MAX),  # MIN-1 wraps to MAX
    ],
)
def test_i32_overflow_wraps(v, expected):
    assert I32(v).value == expected


@pytest.mark.parametrize("v", [1.5, "abc", [1, 2, 3], {1: 2}, object()])
def test_i32_invalid_input_raises(v):
    with pytest.raises((TypeError, RuntimeError, errors.RayforceError)):
        I32(v)


# ── Equality ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1_000_000, -1_000_000, 2**30])
def test_i32_eq_self(v):
    assert I32(v) == I32(v)


@pytest.mark.parametrize("a, b", [(0, 1), (1, 2), (-1, 0), (42, 100), (1_000, 2_000)])
def test_i32_neq(a, b):
    assert I32(a) != I32(b)


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1_000_000])
def test_i32_eq_python_int(v):
    assert I32(v) == v
    assert v == I32(v)


# ── Ordering ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "a, b", [(0, 1), (-1, 0), (1, 2), (-100, 100), (-1_000_000, 1_000_000), (42, 100)]
)
def test_i32_lt(a, b):
    assert (I32(a) < I32(b)).value is True
    assert (I32(b) < I32(a)).value is False


@pytest.mark.parametrize("a, b", [(1, 0), (0, -1), (100, -100), (1_000_000, -1_000_000)])
def test_i32_gt(a, b):
    assert (I32(a) > I32(b)).value is True
    assert (I32(b) > I32(a)).value is False


@pytest.mark.parametrize("a, b", [(0, 0), (1, 1), (-1, 0), (42, 100), (-100, -50)])
def test_i32_le(a, b):
    assert (I32(a) <= I32(b)).value is True


@pytest.mark.parametrize("a, b", [(0, 0), (1, 1), (5, -1), (100, 42), (-50, -100)])
def test_i32_ge(a, b):
    assert (I32(a) >= I32(b)).value is True


# ── Arithmetic ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "a, b, expected",
    [(0, 0, 0), (1, 1, 2), (5, 3, 8), (-5, 3, -2), (-5, -3, -8), (100, 200, 300)],
)
def test_i32_add(a, b, expected):
    assert (I32(a) + I32(b)).value == expected


@pytest.mark.parametrize(
    "a, b, expected", [(5, 3, 2), (3, 5, -2), (0, 0, 0), (-5, -3, -2), (100, 50, 50)]
)
def test_i32_sub(a, b, expected):
    assert (I32(a) - I32(b)).value == expected


@pytest.mark.parametrize(
    "a, b, expected", [(0, 5, 0), (1, 5, 5), (5, 5, 25), (-5, 3, -15), (-5, -3, 15), (10, 10, 100)]
)
def test_i32_mul(a, b, expected):
    assert (I32(a) * I32(b)).value == expected


@pytest.mark.parametrize(
    "a, b, expected", [(10, 4, 2.5), (10, 5, 2.0), (1, 4, 0.25), (-10, 4, -2.5), (100, 10, 10.0)]
)
def test_i32_truediv_returns_f64(a, b, expected):
    assert (I32(a) / I32(b)).value == expected


@pytest.mark.parametrize(
    "a, b, expected", [(10, 4, 2), (10, 3, 3), (1, 4, 0), (-10, 4, -3), (100, 10, 10)]
)
def test_i32_floordiv(a, b, expected):
    assert (I32(a) // I32(b)).value == expected


@pytest.mark.parametrize("a, b, expected", [(10, 3, 1), (10, 5, 0), (7, 3, 1), (100, 7, 2)])
def test_i32_mod(a, b, expected):
    assert (I32(a) % I32(b)).value == expected


# ── Repr / str ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1_000_000, -1_000_000])
def test_i32_repr_contains_value(v):
    assert str(v) in repr(I32(v))


def test_i32_repr_starts_with_class_name():
    assert repr(I32(42)).startswith("I32")


# ── to_python / round-trip ───────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1_000_000, -1_000_000, 2**30])
def test_i32_to_python_returns_int(v):
    out = I32(v).to_python()
    assert isinstance(out, int)
    assert out == v


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1_000_000])
def test_i32_value_attr_matches_to_python(v):
    obj = I32(v)
    assert obj.value == obj.to_python()


# ── Type code ────────────────────────────────────────────────────────────────


def test_i32_type_code_is_negative_4():
    """v2: I32 atom has type code -4."""
    from rayforce import _rayforce_c as r

    assert I32.type_code == -r.TYPE_I32


# ── .value type ──────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1_000_000, -1_000_000])
def test_i32_value_is_int(v):
    assert isinstance(I32(v).value, int)


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1_000_000])
def test_i32_str_contains_value(v):
    assert str(v) in str(I32(v))
