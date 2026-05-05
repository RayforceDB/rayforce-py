"""Comprehensive tests for the Symbol scalar."""

from __future__ import annotations

import pytest

from rayforce import Symbol, errors

# ── Construction ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", ["", "a", "abc", "hello", "world", "rayforce", "kdb+", "test_123"])
def test_symbol_construct_from_str(v):
    assert Symbol(v).value == v


@pytest.mark.parametrize("v", ["a", "abc", "longer_symbol_name", "x" * 100, "x" * 1000])
def test_symbol_various_lengths(v):
    assert Symbol(v).value == v


@pytest.mark.parametrize("v", ["café", "日本語", "emoji_😀", "über", "naïve"])
def test_symbol_unicode(v):
    assert Symbol(v).value == v


@pytest.mark.parametrize("v", ["sym with spaces", "sym!@#$%", "sym\twith\ttabs", "sym\nnewline"])
def test_symbol_special_chars(v):
    assert Symbol(v).value == v


@pytest.mark.parametrize("v, expected_str", [(123, "123"), (1.5, "1.5")])
def test_symbol_construct_from_non_str_coerces(v, expected_str):
    """Symbol() coerces non-string args via str()."""
    assert Symbol(v).value == expected_str


@pytest.mark.parametrize("v", [[1, 2], object()])
def test_symbol_invalid_input_coerces_or_raises(v):
    """Lists/objects either str()-coerce or raise."""
    try:
        result = Symbol(v).value
        assert isinstance(result, str)
    except (TypeError, RuntimeError, errors.RayforceError):
        pass


# ── Equality ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", ["a", "abc", "hello", "rayforce"])
def test_symbol_eq_self(v):
    assert Symbol(v) == Symbol(v)


@pytest.mark.parametrize("a, b", [("a", "b"), ("hello", "world"), ("", "x")])
def test_symbol_neq(a, b):
    assert Symbol(a) != Symbol(b)


@pytest.mark.parametrize("v", ["a", "abc", "hello"])
def test_symbol_eq_python_str(v):
    assert Symbol(v) == v


# ── Interning round-trip ────────────────────────────────────────────────────


@pytest.mark.parametrize("v", ["interned", "shared", "test"])
def test_symbol_interning_round_trip(v):
    assert Symbol(v).value == Symbol(v).value


# ── Repr / str ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", ["a", "abc", "hello", "rayforce"])
def test_symbol_repr_contains_value(v):
    assert v in repr(Symbol(v))


def test_symbol_repr_starts_with_class_name():
    assert repr(Symbol("test")).startswith("Symbol")


# ── to_python / round-trip ───────────────────────────────────────────────────


@pytest.mark.parametrize("v", ["", "a", "abc", "hello", "rayforce", "x" * 100])
def test_symbol_to_python_returns_str(v):
    out = Symbol(v).to_python()
    assert isinstance(out, str)
    assert out == v


@pytest.mark.parametrize("v", ["a", "abc", "hello"])
def test_symbol_value_attr_matches_to_python(v):
    obj = Symbol(v)
    assert obj.value == obj.to_python()


# ── Type code ────────────────────────────────────────────────────────────────


def test_symbol_type_code():
    from rayforce import _rayforce_c as r

    assert Symbol.type_code == -r.TYPE_SYMBOL


# ── .value type ──────────────────────────────────────────────────────────────


@pytest.mark.parametrize("v", ["", "a", "abc", "hello"])
def test_symbol_value_is_str(v):
    assert isinstance(Symbol(v).value, str)


# ── Empty symbol ─────────────────────────────────────────────────────────────


def test_symbol_empty_string():
    assert Symbol("").value == ""


def test_symbol_empty_eq_empty():
    assert Symbol("") == Symbol("")
