"""Coverage for base RayObject contract + previously-untested public methods.

Addresses #L10 (kept public methods, scalar edges) and #L11 (hash/eq).
"""

from __future__ import annotations

import datetime as dt

import pytest

from rayforce import F64, I16, I64, Date, List, String, Symbol, Vector
from rayforce import _rayforce_c as r

# ── get_type_code / from_python (kept public methods) ────────────────────────


def test_get_type_code_matches_obj_type():
    obj = I16(7)
    assert obj.get_type_code() == r.get_obj_type(obj.ptr)


def test_from_python_constructs_scalar():
    assert I64.from_python(42).value == 42
    assert Symbol.from_python("hi").value == "hi"


# ── __hash__ / __eq__ consistency (#L11) ─────────────────────────────────────


def test_equal_scalars_hash_equal():
    assert I64(5) == I64(5)
    assert hash(I64(5)) == hash(I64(5))


def test_scalar_usable_as_dict_key():
    d = {Symbol("a"): 1, Symbol("b"): 2}
    assert d[Symbol("a")] == 1


def test_unequal_scalars_not_equal():
    assert I64(5) != I64(6)


# ── Scalar edge cases (#L10) ─────────────────────────────────────────────────


def test_i64_sentinel_reads_as_none_value():
    # I64 null sentinel is INT64_MIN; it surfaces as a null-valued scalar.
    v = Vector(items=[-(2**63)], ray_type=I64)
    assert v[0].value is None


def test_date_pre_epoch_round_trip():
    # Epoch is 2000-01-01; a date before it (negative days) must round-trip.
    d = Date(dt.date(1999, 6, 15))
    assert d.value == dt.date(1999, 6, 15)


def test_date_to_days_returns_offset():
    # to_days is the raw day offset from the 2000-01-01 epoch.
    assert Date(dt.date(2000, 1, 2)).to_days() == 1
    assert Date(dt.date(1999, 12, 31)).to_days() == -1


def test_string_to_numpy_shape():
    import numpy as np

    arr = String("abc").to_numpy()
    assert isinstance(arr, np.ndarray)


# ── F32 length-1 vector boxing shape ─────────────────────────────────────────


def test_f64_value_round_trip():
    assert F64(2.5).value == 2.5


# ── Fn validation (#L9) ──────────────────────────────────────────────────────


def test_fn_rejects_non_string():
    from rayforce import Fn, errors

    with pytest.raises(errors.RayforceInitError):
        Fn(123)


def test_fn_rejects_non_fn_string():
    from rayforce import Fn, errors

    with pytest.raises(errors.RayforceInitError):
        Fn("(+ 1 2)")


def test_list_to_python_nested():
    inner = List([1, 2])
    outer = List([inner, 3])
    assert len(outer) == 2
    assert isinstance(outer[0], List)
