"""Comprehensive tests for the I16 (signed 16-bit integer) scalar."""

from __future__ import annotations

import pytest

from rayforce import I16, errors

I16_MAX = 2**15 - 1  # 32767
I16_MIN = -(2**15)  # -32768, null sentinel (0Nh)


# ── Construction ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "v",
    [0, 1, -1, 42, -42, 100, 1000, 10_000, -10_000, 32767, -32767],
)
def test_i16_construct_from_int(v):
    assert I16(v).value == v


@pytest.mark.parametrize("v, expected", [(True, 1), (False, 0)])
def test_i16_construct_from_bool(v, expected):
    assert I16(v).value == expected


def test_i16_zero():
    assert I16(0).value == 0


def test_i16_max_value():
    assert I16(I16_MAX).value == I16_MAX


def test_i16_min_is_null_sentinel():
    """I16_MIN (-32768) is the v2 null sentinel (0Nh)."""
    assert I16(I16_MIN).value is None


@pytest.mark.parametrize(
    "v, expected",
    [
        (I16_MAX + 1, None),  # MAX+1 wraps to MIN (null)
        (I16_MIN - 1, I16_MAX),  # MIN-1 wraps to MAX
    ],
)
def test_i16_overflow_wraps(v, expected):
    assert I16(v).value == expected


@pytest.mark.parametrize("v", [1.5, "abc", [1, 2, 3], {1: 2}, object()])
def test_i16_invalid_input_raises(v):
    with pytest.raises((TypeError, RuntimeError, errors.RayforceError)):
        I16(v)


# ── Equality ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, -1, 42, 100, -100, 1000])
def test_i16_eq_self(v):
    assert I16(v) == I16(v)


@pytest.mark.parametrize("a, b", [(0, 1), (1, 2), (-1, 0), (42, 100), (1_000, 2_000)])
def test_i16_neq(a, b):
    assert I16(a) != I16(b)


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1000, -1000])
def test_i16_eq_python_int(v):
    assert I16(v) == v
    assert v == I16(v)


# ── Ordering ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("a, b", [(0, 1), (-1, 0), (1, 2), (-100, 100), (42, 100)])
def test_i16_lt(a, b):
    assert (I16(a) < I16(b)).value is True
    assert (I16(b) < I16(a)).value is False


@pytest.mark.parametrize("a, b", [(1, 0), (0, -1), (100, -100), (1000, -1000)])
def test_i16_gt(a, b):
    assert (I16(a) > I16(b)).value is True


@pytest.mark.parametrize("a, b", [(0, 0), (1, 1), (-1, 0), (42, 100), (-100, -50)])
def test_i16_le(a, b):
    assert (I16(a) <= I16(b)).value is True


@pytest.mark.parametrize("a, b", [(0, 0), (1, 1), (5, -1), (100, 42)])
def test_i16_ge(a, b):
    assert (I16(a) >= I16(b)).value is True


# ── Arithmetic ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "a, b, expected", [(0, 0, 0), (1, 1, 2), (5, 3, 8), (-5, 3, -2), (-5, -3, -8), (100, 200, 300)]
)
def test_i16_add(a, b, expected):
    assert (I16(a) + I16(b)).value == expected


@pytest.mark.parametrize(
    "a, b, expected", [(5, 3, 2), (3, 5, -2), (0, 0, 0), (-5, -3, -2), (100, 50, 50)]
)
def test_i16_sub(a, b, expected):
    assert (I16(a) - I16(b)).value == expected


@pytest.mark.parametrize(
    "a, b, expected", [(0, 5, 0), (1, 5, 5), (5, 5, 25), (-5, 3, -15), (10, 10, 100)]
)
def test_i16_mul(a, b, expected):
    assert (I16(a) * I16(b)).value == expected


@pytest.mark.parametrize(
    "a, b, expected", [(10, 4, 2.5), (10, 5, 2.0), (1, 4, 0.25), (-10, 4, -2.5)]
)
def test_i16_truediv_returns_f64(a, b, expected):
    assert (I16(a) / I16(b)).value == expected


@pytest.mark.parametrize(
    "a, b, expected", [(10, 4, 2), (10, 3, 3), (1, 4, 0), (-10, 4, -3), (100, 10, 10)]
)
def test_i16_floordiv(a, b, expected):
    assert (I16(a) // I16(b)).value == expected


@pytest.mark.parametrize("a, b, expected", [(10, 3, 1), (10, 5, 0), (7, 3, 1)])
def test_i16_mod(a, b, expected):
    assert (I16(a) % I16(b)).value == expected


# ── Repr / str ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1000, -1000])
def test_i16_repr_contains_value(v):
    assert str(v) in repr(I16(v))


def test_i16_repr_starts_with_class_name():
    assert repr(I16(42)).startswith("I16")


# ── to_python / round-trip ───────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1000, -1000, 32767])
def test_i16_to_python_returns_int(v):
    out = I16(v).to_python()
    assert isinstance(out, int)
    assert out == v


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1000])
def test_i16_value_attr_matches_to_python(v):
    obj = I16(v)
    assert obj.value == obj.to_python()


# ── Type code ────────────────────────────────────────────────────────────────


def test_i16_type_code_is_negative_3():
    from rayforce import _rayforce_c as r

    assert I16.type_code == -r.TYPE_I16


# ── .value type ──────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1000, -1000])
def test_i16_value_is_int(v):
    assert isinstance(I16(v).value, int)


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1000])
def test_i16_str_contains_value(v):
    assert str(v) in str(I16(v))
