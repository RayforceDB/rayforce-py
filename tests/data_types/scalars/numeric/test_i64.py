"""Comprehensive tests for the I64 (signed 64-bit integer) scalar."""

from __future__ import annotations

import pytest

from rayforce import F64, I64, errors

I64_MAX = 2**63 - 1
I64_MIN = -(2**63)  # null sentinel (0Nj)


# ── Construction ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "v",
    [0, 1, -1, 42, -42, 100, 1000, 1_000_000, -1_000_000, 2**32, -(2**32), 2**62, -(2**62)],
)
def test_i64_construct_from_int(v):
    assert I64(v).value == v


@pytest.mark.parametrize("v, expected", [(True, 1), (False, 0)])
def test_i64_construct_from_bool(v, expected):
    assert I64(v).value == expected


@pytest.mark.parametrize("v", [0.0, 1.5, -1.5, 3.99, -3.99, 42.7])
def test_i64_construct_from_float_rejected(v):
    """v2 init_i64 only accepts ints, not floats."""
    with pytest.raises((TypeError, RuntimeError, errors.RayforceError)):
        I64(v)


def test_i64_zero():
    assert I64(0).value == 0


def test_i64_max_value():
    assert I64(I64_MAX).value == I64_MAX


def test_i64_min_is_null_sentinel():
    """I64_MIN (0x8000…0000) is the v2 null sentinel."""
    assert I64(I64_MIN).value is None


@pytest.mark.parametrize("v", [I64_MAX + 1, I64_MIN - 1, 2**80, -(2**80)])
def test_i64_overflow_raises(v):
    with pytest.raises((RuntimeError, OverflowError)):
        I64(v)


@pytest.mark.parametrize("v", ["abc", [1, 2, 3], {1: 2}, object()])
def test_i64_invalid_input_raises(v):
    with pytest.raises((TypeError, RuntimeError, errors.RayforceError)):
        I64(v)


# ── Equality ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1_000_000, -1_000_000, 2**62])
def test_i64_eq_self(v):
    assert I64(v) == I64(v)


@pytest.mark.parametrize("a, b", [(0, 1), (1, 2), (-1, 0), (42, 100), (1_000, 2_000)])
def test_i64_neq(a, b):
    assert I64(a) != I64(b)


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1_000_000])
def test_i64_eq_python_int(v):
    assert I64(v) == v
    assert v == I64(v)


# ── Ordering ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "a, b", [(0, 1), (-1, 0), (1, 2), (-100, 100), (-1_000_000, 1_000_000), (42, 100)]
)
def test_i64_lt(a, b):
    assert (I64(a) < I64(b)).value is True
    assert (I64(b) < I64(a)).value is False


@pytest.mark.parametrize("a, b", [(1, 0), (0, -1), (100, -100), (1_000_000, -1_000_000)])
def test_i64_gt(a, b):
    assert (I64(a) > I64(b)).value is True
    assert (I64(b) > I64(a)).value is False


@pytest.mark.parametrize("a, b", [(0, 0), (1, 1), (-1, 0), (42, 100), (-100, -50)])
def test_i64_le(a, b):
    assert (I64(a) <= I64(b)).value is True


@pytest.mark.parametrize("a, b", [(0, 0), (1, 1), (5, -1), (100, 42), (-50, -100)])
def test_i64_ge(a, b):
    assert (I64(a) >= I64(b)).value is True


# ── Arithmetic ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (0, 0, 0),
        (1, 1, 2),
        (5, 3, 8),
        (-5, 3, -2),
        (-5, -3, -8),
        (100, 200, 300),
        (1_000_000, 2_000_000, 3_000_000),
    ],
)
def test_i64_add(a, b, expected):
    assert (I64(a) + I64(b)).value == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [(5, 3, 2), (3, 5, -2), (0, 0, 0), (-5, -3, -2), (100, 50, 50), (1_000_000, 1, 999_999)],
)
def test_i64_sub(a, b, expected):
    assert (I64(a) - I64(b)).value == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [(0, 5, 0), (1, 5, 5), (5, 5, 25), (-5, 3, -15), (-5, -3, 15), (10, 10, 100), (100, 0, 0)],
)
def test_i64_mul(a, b, expected):
    assert (I64(a) * I64(b)).value == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (10, 4, 2.5),
        (10, 5, 2.0),
        (1, 4, 0.25),
        (-10, 4, -2.5),
        (100, 10, 10.0),
    ],
)
def test_i64_truediv(a, b, expected):
    """v2 `/` does true division, returns F64."""
    assert (I64(a) / I64(b)).value == expected


@pytest.mark.parametrize(
    "a, b, expected", [(10, 4, 2), (10, 3, 3), (1, 4, 0), (-10, 4, -3), (100, 10, 10)]
)
def test_i64_floordiv(a, b, expected):
    """v2 `//` does floor division, returns I64."""
    assert (I64(a) // I64(b)).value == expected


@pytest.mark.parametrize(
    "a, b, expected", [(10, 3, 1), (10, 5, 0), (7, 3, 1), (-7, 3, 2), (100, 7, 2)]
)
def test_i64_mod(a, b, expected):
    assert (I64(a) % I64(b)).value == expected


# ── Mixed-type arithmetic ────────────────────────────────────────────────────


@pytest.mark.parametrize("a, b", [(I64(5), 3), (I64(10), 7), (I64(-1), 5)])
def test_i64_add_python_int(a, b):
    assert (a + b).value == a.value + b


@pytest.mark.parametrize("a, b", [(5, I64(3)), (10, I64(7))])
def test_i64_radd_python_int(a, b):
    assert (a + b).value == a + b.value


def test_i64_add_f64_returns_f64():
    result = I64(5) + F64(2.5)
    assert result.value == 7.5
    assert isinstance(result, F64)


# ── Repr / str ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1_000_000, -1_000_000])
def test_i64_repr_contains_value(v):
    assert str(v) in repr(I64(v))


def test_i64_repr_starts_with_class_name():
    assert repr(I64(42)).startswith("I64")


# ── to_python / round-trip ───────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1_000_000, -1_000_000, 2**62])
def test_i64_to_python_returns_int(v):
    out = I64(v).to_python()
    assert isinstance(out, int)
    assert out == v


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1_000_000, -1_000_000])
def test_i64_value_attr_matches_to_python(v):
    obj = I64(v)
    assert obj.value == obj.to_python()


# ── Type code ────────────────────────────────────────────────────────────────


def test_i64_type_code_is_negative_5():
    """v2: I64 atom has type code -5."""
    from rayforce import _rayforce_c as r

    assert I64.type_code == -r.TYPE_I64


# ── .value type ──────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1_000_000, -1_000_000])
def test_i64_value_is_int(v):
    assert isinstance(I64(v).value, int)


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1_000_000])
def test_i64_str_contains_value(v):
    assert str(v) in str(I64(v))
