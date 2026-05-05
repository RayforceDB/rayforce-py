"""Comprehensive tests for the B8 (boolean) scalar."""

from __future__ import annotations

import pytest

from rayforce import B8

# ── Construction ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v, expected", [(True, True), (False, False)])
def test_b8_construct_from_bool(v, expected):
    assert B8(v).value is expected


@pytest.mark.parametrize(
    "v, expected", [(0, False), (1, True), (-1, True), (42, True), (100, True)]
)
def test_b8_construct_from_int_truthy(v, expected):
    assert B8(v).value is expected


def test_b8_true():
    assert B8(True).value is True


def test_b8_false():
    assert B8(False).value is False


# ── Equality ─────────────────────────────────────────────────────────────────


def test_b8_true_eq_true():
    assert B8(True) == B8(True)


def test_b8_false_eq_false():
    assert B8(False) == B8(False)


def test_b8_true_neq_false():
    assert B8(True) != B8(False)


@pytest.mark.parametrize("v", [True, False])
def test_b8_eq_python_bool(v):
    assert B8(v) == v
    assert v == B8(v)


# ── Repr / str ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [True, False])
def test_b8_repr_contains_value(v):
    assert str(v) in repr(B8(v))


def test_b8_repr_starts_with_class_name():
    assert repr(B8(True)).startswith("B8")


# ── to_python ────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [True, False])
def test_b8_to_python_returns_bool(v):
    out = B8(v).to_python()
    assert isinstance(out, bool)
    assert out is v


@pytest.mark.parametrize("v", [True, False])
def test_b8_value_attr_matches_to_python(v):
    obj = B8(v)
    assert obj.value == obj.to_python()


# ── Type code ────────────────────────────────────────────────────────────────


def test_b8_type_code_is_negative_1():
    from rayforce import _rayforce_c as r

    assert B8.type_code == -r.TYPE_B8


# ── .value type ──────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", [True, False])
def test_b8_value_is_bool(v):
    assert isinstance(B8(v).value, bool)


# ── Identity ─────────────────────────────────────────────────────────────────


def test_b8_distinct_instances_eq():
    a = B8(True)
    b = B8(True)
    assert a == b


def test_b8_value_is_python_bool_singleton():
    assert B8(True).value is True
    assert B8(False).value is False
