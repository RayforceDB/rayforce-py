import pytest

from rayforce import _rayforce_c as r
from rayforce import errors
from rayforce import types as t
from rayforce.types.registry import TypeRegistry


def test_register_and_get():
    TypeRegistry.register(-9999, t.I16)
    assert TypeRegistry.get(-9999) == t.I16
    assert TypeRegistry.is_registered(-9999)


def test_register_duplicate_same_class():
    TypeRegistry.register(-9998, t.I32)
    TypeRegistry.register(-9998, t.I32)
    assert TypeRegistry.get(-9998) == t.I32


def test_register_duplicate_different_class():
    TypeRegistry.register(-9997, t.I16)
    with pytest.raises(errors.RayforceTypeRegistryError):
        TypeRegistry.register(-9997, t.I32)


def test_is_registered():
    assert not TypeRegistry.is_registered(-9996)
    TypeRegistry.register(-9996, t.I64)
    assert TypeRegistry.is_registered(-9996)


def test_list_registered_types():
    registered = TypeRegistry.list_registered_types()
    assert isinstance(registered, dict)
    assert -r.TYPE_I16 in registered
    assert registered[-r.TYPE_I16] == "I16"


def test_from_ptr_scalar():
    result = TypeRegistry.from_ptr(t.I16(42).ptr)
    assert isinstance(result, t.I16)
    assert result.value == 42


def test_from_ptr_vector():
    result = TypeRegistry.from_ptr(t.Vector(ray_type=t.Symbol, items=["test1", "test2"]).ptr)
    assert isinstance(result, t.Vector)
    assert len(result) == 2


def test_from_ptr_invalid_object():
    with pytest.raises(Exception, match="Expected RayObject"):
        TypeRegistry.from_ptr("not a RayObject")
