"""Round-trip tests for the binary serialize/deserialize surface (#H5).

ser_obj/de_obj had zero coverage despite being a public binary-format API.
"""

from __future__ import annotations

import pytest

from rayforce import B8, F64, I16, I32, I64, U8, Dict, List, Symbol, Table, Vector
from rayforce.ffi import FFI
from rayforce.utils.conversion import ray_to_python


def _round_trip(obj):
    """ser → de → return the rehydrated RayObject."""
    serialized = FFI.ser_obj(obj.ptr)
    return ray_to_python(FFI.de_obj(serialized))


@pytest.mark.parametrize(
    "vec",
    [
        Vector(items=[1, 2, 3], ray_type=I16),
        Vector(items=[10, 20, 30], ray_type=I32),
        Vector(items=[100, 200, 300], ray_type=I64),
        Vector(items=[1.5, 2.5, 3.5], ray_type=F64),
        Vector(items=[0, 1, 255], ray_type=U8),
        Vector(items=[True, False, True], ray_type=B8),
        Vector(items=["a", "b", "c"], ray_type=Symbol),
    ],
)
def test_serde_vector_round_trip(vec):
    out = _round_trip(vec)
    assert [el.value if hasattr(el, "value") else el for el in out] == [
        el.value if hasattr(el, "value") else el for el in vec
    ]


def test_serde_scalar_round_trip():
    assert _round_trip(I64(42)).value == 42
    assert _round_trip(F64(3.14)).value == 3.14
    assert _round_trip(Symbol("hello")).value == "hello"


def test_serde_list_round_trip():
    lst = List([1, "a", 3.5, True])
    out = _round_trip(lst)
    assert len(out) == 4
    assert out[0].value == 1
    assert out[1].value == "a"


def test_serde_dict_round_trip():
    d = Dict({"a": 1, "b": 2})
    out = _round_trip(d)
    assert out["a"] == 1
    assert out["b"] == 2


def test_serde_table_round_trip():
    tbl = Table(
        {
            "id": Vector(items=[1, 2, 3], ray_type=I64),
            "name": Vector(items=["x", "y", "z"], ray_type=Symbol),
        }
    )
    out = _round_trip(tbl)
    assert isinstance(out, Table)
    assert len(out) == 3


def test_serde_empty_vector_round_trip():
    out = _round_trip(Vector(items=[], ray_type=I64))
    assert len(out) == 0


def test_de_obj_on_garbage_raises():
    # Deserializing a non-serialized object should error, not crash.
    garbage = Vector(items=[1, 2, 3], ray_type=U8)
    with pytest.raises(Exception):
        FFI.de_obj(garbage.ptr)
