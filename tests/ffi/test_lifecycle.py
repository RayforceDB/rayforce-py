"""FFI tests covering lifecycle, identity, and reference-count behavior."""

from __future__ import annotations

import pytest

from rayforce import I64, Vector
from rayforce import _rayforce_c as r
from rayforce.ffi import FFI

# ── obj_addr identity ───────────────────────────────────────────────────────


def test_obj_addr_returns_int():
    obj = FFI.init_i64(42)
    addr = FFI.obj_addr(obj)
    assert isinstance(addr, int)
    assert addr > 0


@pytest.mark.parametrize("v", [0, 1, -1, 42, 1_000_000])
def test_obj_addr_distinct_for_distinct_objects(v):
    """Each fresh init_i64 gets a separate ray_t* address."""
    a = FFI.init_i64(v)
    b = FFI.init_i64(v)
    assert FFI.obj_addr(a) != FFI.obj_addr(b)


# ── get_obj_type ────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "ctor, expected_type",
    [
        (FFI.init_i16, -r.TYPE_I16),
        (FFI.init_i32, -r.TYPE_I32),
        (FFI.init_i64, -r.TYPE_I64),
        (FFI.init_u8, -r.TYPE_U8),
    ],
)
def test_get_obj_type_for_int_atoms(ctor, expected_type):
    assert FFI.get_obj_type(ctor(42)) == expected_type


def test_get_obj_type_f64_atom():
    assert FFI.get_obj_type(FFI.init_f64(3.14)) == -r.TYPE_F64


def test_get_obj_type_b8_atom():
    assert FFI.get_obj_type(FFI.init_b8(True)) == -r.TYPE_B8


def test_get_obj_type_symbol_atom():
    assert FFI.get_obj_type(FFI.init_symbol("hello")) == -r.TYPE_SYMBOL


def test_get_obj_type_string_atom():
    assert FFI.get_obj_type(FFI.init_string("hello")) == -r.TYPE_STR


# ── get_obj_length ──────────────────────────────────────────────────────────


@pytest.mark.parametrize("items", [[1, 2, 3], list(range(10)), list(range(100))])
def test_get_obj_length_int_vector(items):
    v = Vector(items=items, ray_type=I64)
    assert FFI.get_obj_length(v.ptr) == len(items)


def test_get_obj_length_empty_vector():
    v = FFI.init_vector(r.TYPE_I64, 0)
    assert FFI.get_obj_length(v) == 0


# ── rc_obj (reference count) ────────────────────────────────────────────────


def test_rc_obj_returns_int():
    obj = FFI.init_i64(42)
    rc = FFI.rc_obj(obj)
    assert isinstance(rc, int)
    assert rc > 0


# ── Slice ────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "items, offset, length",
    [
        ([1, 2, 3, 4, 5], 0, 3),
        ([1, 2, 3, 4, 5], 1, 3),
        ([1, 2, 3, 4, 5], 2, 2),
        (list(range(20)), 5, 10),
    ],
)
def test_vec_slice(items, offset, length):
    src = Vector(items=items, ray_type=I64)
    sliced = FFI.vec_slice(src.ptr, offset, length)
    assert FFI.get_obj_length(sliced) == length


# ── Null bitmap ─────────────────────────────────────────────────────────────


def test_vec_set_null_and_check():
    v = Vector(items=[1, 2, 3, 4, 5], ray_type=I64)
    FFI.vec_set_null(v.ptr, 2, is_null=True)
    assert FFI.vec_is_null(v.ptr, 2) is True
    assert FFI.vec_is_null(v.ptr, 0) is False


@pytest.mark.parametrize("idx", [0, 1, 2, 3, 4])
def test_vec_set_null_each_idx(idx):
    v = Vector(items=[10, 20, 30, 40, 50], ray_type=I64)
    FFI.vec_set_null(v.ptr, idx, is_null=True)
    assert FFI.vec_is_null(v.ptr, idx) is True


def test_vec_set_null_then_unset():
    v = Vector(items=[1, 2, 3], ray_type=I64)
    FFI.vec_set_null(v.ptr, 1, is_null=True)
    assert FFI.vec_is_null(v.ptr, 1) is True
    FFI.vec_set_null(v.ptr, 1, is_null=False)
    assert FFI.vec_is_null(v.ptr, 1) is False
