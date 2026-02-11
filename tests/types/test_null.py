import pytest

from rayforce import FFI, Dict, I64, List, Vector, eval_obj
from rayforce import _rayforce_c as r
from rayforce.types import Null, Table
from rayforce.types.operators import Operation
from rayforce.types.registry import TypeRegistry


def test_null_to_python():
    assert Null.to_python() is None


def test_null_in_vector():
    vec = Vector(ray_type=Null, items=[Null, Null])

    assert len(vec) == 2
    assert FFI.get_obj_type(vec.ptr) == 0
    assert vec[0] is vec[1] is Null


def test_null_in_table():
    table = Table({"null_col": Vector(ray_type=Null, items=[Null, Null, Null])})

    assert isinstance(table, Table)
    assert len(table.columns()) == 1
    assert len(table.values()) == 1

    null_col = table.values()[0]
    assert len(null_col) == 3
    assert all(null_col[i] is Null for i in range(3))
    assert all(null_col[i].to_python() is None for i in range(3))


def test_null_registry_from_ptr():
    result = TypeRegistry.from_ptr(r.NULL_OBJ)
    assert result is Null


# ---------------------------------------------------------------------------
# Null in List container
# ---------------------------------------------------------------------------


def test_null_in_list():
    """Null values can be stored in a List container."""
    lst = List([Null, I64(42), Null])
    assert len(lst) == 3
    assert lst[0] is Null
    assert lst[1].value == 42
    assert lst[2] is Null


def test_null_in_list_all_nulls():
    """A List containing only Null values."""
    lst = List([Null, Null, Null])
    assert len(lst) == 3
    for i in range(3):
        assert lst[i] is Null
        assert lst[i].to_python() is None


def test_null_append_to_list():
    """Null can be appended to an existing List."""
    lst = List([I64(1)])
    lst.append(Null)
    assert len(lst) == 2
    assert lst[1] is Null


# ---------------------------------------------------------------------------
# Null in Dict container
# ---------------------------------------------------------------------------


def test_null_in_dict_value():
    """Dict can contain Null as a value."""
    d = Dict({"key1": 42, "key2": None})
    assert len(d) == 2
    # The None should have been converted to Null
    val = d["key2"]
    assert val is Null or val is None or (hasattr(val, "to_python") and val.to_python() is None)


def test_null_in_dict_multiple_null_values():
    """Dict with multiple Null values."""
    d = Dict({"a": None, "b": None, "c": 10})
    assert len(d) == 3
    c_val = d["c"]
    assert hasattr(c_val, "value") and c_val.value == 10


# ---------------------------------------------------------------------------
# Null in arithmetic operations
# ---------------------------------------------------------------------------


def test_null_add_i64_raises():
    """Adding Null to an integer raises a type error (Null is not numeric)."""
    from rayforce.errors import RayforceTypeError

    with pytest.raises(RayforceTypeError):
        eval_obj(List([Operation.ADD, Null, I64(5)]))


def test_null_subtract_i64_raises():
    """Subtracting with Null raises a type error."""
    from rayforce.errors import RayforceTypeError

    with pytest.raises(RayforceTypeError):
        eval_obj(List([Operation.SUBTRACT, I64(10), Null]))


def test_null_multiply_i64_raises():
    """Multiplying with Null raises a type error."""
    from rayforce.errors import RayforceTypeError

    with pytest.raises(RayforceTypeError):
        eval_obj(List([Operation.MULTIPLY, Null, I64(3)]))


def test_null_add_null_raises():
    """Adding Null to Null also raises a type error (Null is not arithmetic)."""
    from rayforce.errors import RayforceTypeError

    with pytest.raises(RayforceTypeError):
        eval_obj(List([Operation.ADD, Null, Null]))


def test_null_equality():
    """Null equality comparisons."""
    assert Null == None  # noqa: E711
    assert Null == Null
    assert not Null  # Null is falsy


def test_null_repr():
    """Null repr and str."""
    assert repr(Null) == "Null"
    assert str(Null) == "Null"


def test_null_type_code():
    """Null has the correct type code."""
    assert Null.type_code == r.TYPE_NULL


def test_null_ptr():
    """Null ptr is the NULL_OBJ sentinel."""
    assert Null.ptr is r.NULL_OBJ
