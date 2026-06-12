"""Comprehensive tests for utils.python_to_ray and ray_to_python."""

from __future__ import annotations

import pytest

from rayforce import (
    B8,
    F64,
    I64,
    U8,
    Symbol,
    Vector,
    python_to_ray,
    ray_to_python,
)

# ── python_to_ray: scalars ───────────────────────────────────────────────────


@pytest.mark.parametrize("v", [True, False])
def test_python_to_ray_bool(v):
    obj = python_to_ray(v)
    assert ray_to_python(obj) == v


@pytest.mark.parametrize("v", [0, 1, -1, 42, 100, 1_000_000, -1_000_000])
def test_python_to_ray_int(v):
    obj = python_to_ray(v)
    assert ray_to_python(obj) == v


@pytest.mark.parametrize("v", [0.0, 1.5, -1.5, 3.14, -3.14, 1e10, 1e-10])
def test_python_to_ray_float(v):
    obj = python_to_ray(v)
    assert ray_to_python(obj) == pytest.approx(v)


@pytest.mark.parametrize("v", ["", "a", "abc", "hello", "world"])
def test_python_to_ray_str(v):
    obj = python_to_ray(v)
    out = ray_to_python(obj)
    assert out == v


# ── python_to_ray: containers ────────────────────────────────────────────────


@pytest.mark.parametrize(
    "items",
    [
        [],
        [1],
        [1, 2, 3],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [-1, 0, 1],
        list(range(20)),
    ],
)
def test_python_to_ray_int_list(items):
    obj = python_to_ray(items)
    out = ray_to_python(obj)
    assert [getattr(v, "value", v) for v in out] == items


@pytest.mark.parametrize("items", [[1.5, 2.5, 3.5], [0.0, 1.0, -1.0], [1e-10, 1e10, 1.0]])
def test_python_to_ray_float_list(items):
    obj = python_to_ray(items)
    out = ray_to_python(obj)
    assert [getattr(v, "value", v) for v in out] == pytest.approx(items)


@pytest.mark.parametrize("items", [["a"], ["a", "b"], ["x", "y", "z"], ["hello", "world"]])
def test_python_to_ray_str_list(items):
    obj = python_to_ray(items)
    out = ray_to_python(obj)
    assert [str(getattr(v, "value", v)) for v in out] == items


@pytest.mark.parametrize("items", [[1, "a", 1.5], [True, 1, "x"], [None, 1, "a"]])
def test_python_to_ray_mixed_list(items):
    """Mixed-type list goes through general LIST path."""
    obj = python_to_ray(items)
    out = ray_to_python(obj)
    assert len(out) == len(items)


# ── python_to_ray: dict ──────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "d",
    [
        {"a": 1},
        {"a": 1, "b": 2},
        {"x": 10, "y": 20, "z": 30},
        {"key": "value"},
    ],
)
def test_python_to_ray_dict(d):
    obj = python_to_ray(d)
    out = ray_to_python(obj)
    assert dict(out) is not None  # at minimum doesn't crash


# ── ray_to_python: scalar round-trips ───────────────────────────────────────


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1_000_000])
def test_ray_to_python_i64_scalar(v):
    assert ray_to_python(I64(v).ptr) == v


@pytest.mark.parametrize("v", [0.0, 1.5, -1.5, 3.14])
def test_ray_to_python_f64_scalar(v):
    assert ray_to_python(F64(v).ptr) == v


@pytest.mark.parametrize("v", [True, False])
def test_ray_to_python_b8_scalar(v):
    assert ray_to_python(B8(v).ptr) == v


@pytest.mark.parametrize("v", [0, 1, 100, 255])
def test_ray_to_python_u8_scalar(v):
    assert ray_to_python(U8(v).ptr) == v


@pytest.mark.parametrize("v", ["", "a", "abc", "hello"])
def test_ray_to_python_symbol(v):
    out = ray_to_python(Symbol(v).ptr)
    assert str(out) == v


# ── Round-trip via Vector ────────────────────────────────────────────────────


@pytest.mark.parametrize("items", [[1, 2, 3], [10, 20, 30, 40, 50], list(range(50))])
def test_round_trip_i64_vector(items):
    v = Vector(items=items, ray_type=I64)
    out = [el.value for el in v]
    assert out == items


@pytest.mark.parametrize("items", [[1.5, 2.5], [0.0, 1.0, -1.0], [1e-10, 1e10]])
def test_round_trip_f64_vector(items):
    v = Vector(items=items, ray_type=F64)
    out = [el.value for el in v]
    assert out == pytest.approx(items)


@pytest.mark.parametrize("items", [[True, False, True], [False, False, True]])
def test_round_trip_b8_vector(items):
    v = Vector(items=items, ray_type=B8)
    out = [el.value for el in v]
    assert out == items


@pytest.mark.parametrize("items", [["a"], ["a", "b", "c"], ["foo", "bar", "baz"]])
def test_round_trip_symbol_vector(items):
    v = Vector(items=items, ray_type=Symbol)
    out = [str(el.value) for el in v]
    assert out == items


# ── None / Null ──────────────────────────────────────────────────────────────


def test_python_to_ray_none():
    obj = python_to_ray(None)
    assert obj is not None  # produces NULL_OBJ or similar
