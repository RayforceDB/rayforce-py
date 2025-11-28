import pytest
from rayforce import _rayforce_c as r
from rayforce.types.registry import TypeRegistry
from rayforce.types import exceptions
from rayforce import types as t


def test_register_and_get():
    test_type_code = -9999
    test_class = t.I16

    TypeRegistry.register(test_type_code, test_class)
    assert TypeRegistry.get(test_type_code) == test_class
    assert TypeRegistry.is_registered(test_type_code)


def test_register_duplicate_same_class():
    test_type_code = -9998
    test_class = t.I32

    TypeRegistry.register(test_type_code, test_class)
    TypeRegistry.register(test_type_code, test_class)
    assert TypeRegistry.get(test_type_code) == test_class


def test_register_duplicate_different_class():
    test_type_code = -9997
    TypeRegistry.register(test_type_code, t.I16)

    with pytest.raises(exceptions.RayTypeRegistryException):
        TypeRegistry.register(test_type_code, t.I32)


def test_is_registered():
    test_type_code = -9996
    assert not TypeRegistry.is_registered(test_type_code)

    TypeRegistry.register(test_type_code, t.I64)
    assert TypeRegistry.is_registered(test_type_code)


def test_list_registered_types():
    registered = TypeRegistry.list_registered_types()
    assert isinstance(registered, dict)

    assert -r.TYPE_I16 in registered
    assert registered[-r.TYPE_I16] == "I16"


def test_from_ptr_scalar():
    i16_obj = t.I16(42)
    result = TypeRegistry.from_ptr(i16_obj.ptr)

    assert isinstance(result, t.I16)
    assert result.value == 42


def test_from_ptr_vector():
    vec = t.Vector(type_code=t.Symbol.type_code, items=["test1", "test2"])
    result = TypeRegistry.from_ptr(vec.ptr)

    assert isinstance(result, t.Vector)
    assert len(result) == 2


def test_from_ptr_invalid_object():
    with pytest.raises(Exception, match="Expected RayObject"):
        TypeRegistry.from_ptr("not a RayObject")
