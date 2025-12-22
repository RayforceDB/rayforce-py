import pytest
from rayforce import _rayforce_c as r
from rayforce.types import Null, Vector, Table
from rayforce.types.registry import TypeRegistry
from rayforce.types.scalars import Symbol, I64


def test_null_to_python():
    assert Null.to_python() is None


def test_null_in_vector():
    vec = Vector(ray_type=Null, items=[Null, Null])

    assert len(vec) == 2
    assert vec.ptr.get_obj_type() == 0  # Vector became a list

    assert vec[0] == Null
    assert vec[1] == Null

    assert vec[0] is vec[1]


def test_null_in_table():
    table = Table.from_dict({"test": Vector(ray_type=Null, items=[Null, Null])})

    assert isinstance(table, Table)
    columns = table.columns()
    assert len(columns) == 1

    values = table.values()
    assert len(values) == 1

    null_col = values[0]
    assert len(null_col) == 2
    assert null_col[0] is null_col[1] is Null


def test_null_table_values():
    table = Table.from_dict({"null_col": Vector(ray_type=Null, items=[Null, Null, Null])})

    values = table.values()
    null_col = values[0]

    # Test that all values are Null
    for i in range(3):
        assert null_col[i] == Null
        assert null_col[i].to_python() is None


def test_null_registry_from_ptr():
    result = TypeRegistry.from_ptr(r.NULL_OBJ)
    assert result is Null


def test_null_singleton():
    from rayforce.types import Null as Null2

    assert Null is Null2
    assert Null is Null
