"""Comprehensive tests for the U8 (unsigned 8-bit integer / byte) scalar."""

from __future__ import annotations

import pytest

from rayforce import U8, errors

U8_MAX = 255
U8_MIN = 0


# ── Construction ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, 42, 100, 127, 128, 200, 255])
def test_u8_construct_from_int(v):
    assert U8(v).value == v


@pytest.mark.parametrize("v, expected", [(True, 1), (False, 0)])
def test_u8_construct_from_bool(v, expected):
    assert U8(v).value == expected


def test_u8_min_value():
    assert U8(0).value == 0


def test_u8_max_value():
    assert U8(U8_MAX).value == U8_MAX


@pytest.mark.parametrize(
    "v, expected", [(256, 0), (257, 1), (300, 44), (-1, 255), (-2, 254), (511, 255)]
)
def test_u8_overflow_wraps_modulo_256(v, expected):
    assert U8(v).value == expected


@pytest.mark.parametrize("v", ["abc", [1, 2, 3], {1: 2}, object()])
def test_u8_invalid_input_raises(v):
    with pytest.raises((TypeError, ValueError, RuntimeError, errors.RayforceError)):
        U8(v)


@pytest.mark.parametrize("v, expected", [(1.5, 1), (3.7, 3), (10.99, 10)])
def test_u8_float_truncates(v, expected):
    """U8 accepts floats and truncates to int."""
    assert U8(v).value == expected


# ── Equality ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, 42, 100, 200, 255])
def test_u8_eq_self(v):
    assert U8(v) == U8(v)


@pytest.mark.parametrize("a, b", [(0, 1), (1, 2), (42, 100), (200, 255)])
def test_u8_neq(a, b):
    assert U8(a) != U8(b)


@pytest.mark.parametrize("v", [0, 1, 42, 100, 200, 255])
def test_u8_eq_python_int(v):
    assert U8(v) == v
    assert v == U8(v)


# ── Ordering ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("a, b", [(0, 1), (1, 2), (42, 100), (100, 200), (200, 255)])
def test_u8_lt(a, b):
    assert (U8(a) < U8(b)).value is True
    assert (U8(b) < U8(a)).value is False


@pytest.mark.parametrize("a, b", [(255, 0), (200, 100), (100, 42)])
def test_u8_gt(a, b):
    assert (U8(a) > U8(b)).value is True


@pytest.mark.parametrize("a, b", [(0, 0), (1, 1), (42, 100), (200, 200)])
def test_u8_le(a, b):
    assert (U8(a) <= U8(b)).value is True


@pytest.mark.parametrize("a, b", [(0, 0), (1, 1), (255, 0), (100, 42)])
def test_u8_ge(a, b):
    assert (U8(a) >= U8(b)).value is True


# ── Arithmetic ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "a, b, expected",
    [(0, 0, 0), (1, 1, 2), (5, 3, 8), (100, 50, 150), (10, 20, 30), (200, 50, 250)],
)
def test_u8_add(a, b, expected):
    assert (U8(a) + U8(b)).value == expected


@pytest.mark.parametrize("a, b, expected", [(5, 3, 2), (10, 5, 5), (100, 50, 50), (255, 0, 255)])
def test_u8_sub(a, b, expected):
    assert (U8(a) - U8(b)).value == expected


@pytest.mark.parametrize(
    "a, b, expected", [(0, 5, 0), (1, 5, 5), (5, 5, 25), (10, 10, 100), (15, 15, 225)]
)
def test_u8_mul(a, b, expected):
    assert (U8(a) * U8(b)).value == expected


@pytest.mark.parametrize(
    "a, b, expected", [(10, 4, 2.5), (10, 5, 2.0), (1, 4, 0.25), (100, 10, 10.0)]
)
def test_u8_truediv_returns_f64(a, b, expected):
    assert (U8(a) / U8(b)).value == expected


@pytest.mark.parametrize("a, b, expected", [(10, 4, 2), (10, 3, 3), (1, 4, 0), (100, 10, 10)])
def test_u8_floordiv(a, b, expected):
    assert (U8(a) // U8(b)).value == expected


@pytest.mark.parametrize("a, b, expected", [(10, 3, 1), (10, 5, 0), (7, 3, 1), (100, 7, 2)])
def test_u8_mod(a, b, expected):
    assert (U8(a) % U8(b)).value == expected


# ── Repr / str ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, 42, 100, 200, 255])
def test_u8_repr_contains_value(v):
    assert str(v) in repr(U8(v))


def test_u8_repr_starts_with_class_name():
    assert repr(U8(42)).startswith("U8")


# ── to_python / round-trip ───────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, 42, 100, 200, 255])
def test_u8_to_python_returns_int(v):
    out = U8(v).to_python()
    assert isinstance(out, int)
    assert out == v


@pytest.mark.parametrize("v", [0, 1, 42, 100, 200, 255])
def test_u8_value_attr_matches_to_python(v):
    obj = U8(v)
    assert obj.value == obj.to_python()


# ── Type code ────────────────────────────────────────────────────────────────


def test_u8_type_code_is_negative_2():
    from rayforce import _rayforce_c as r

    assert U8.type_code == -r.TYPE_U8


# ── .value type ──────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, 42, 100, 200, 255])
def test_u8_value_is_int(v):
    assert isinstance(U8(v).value, int)


@pytest.mark.parametrize("v", [0, 1, 42, 100, 200, 255])
def test_u8_str_contains_value(v):
    assert str(v) in str(U8(v))


# ── Range ────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", list(range(0, 256, 17)))  # 0, 17, 34, …, 255
def test_u8_full_range_construction(v):
    assert U8(v).value == v
