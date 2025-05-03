import pytest

from raypy import _rayforce as r
from raypy.types.bool import b8


class TestBoolTypes:
    def test_b8_creation(self):
        """Test creation of b8 booleans with different inputs."""
        # Test with boolean values
        true_value = b8(True)
        assert true_value.value is True
        assert type(true_value.value) == bool
        assert true_value.ptr.get_type() == -r.TYPE_B8

        false_value = b8(False)
        assert false_value.value is False
        assert type(false_value.value) == bool
        assert false_value.ptr.get_type() == -r.TYPE_B8

        # Test with integers (should be converted to boolean)
        one_value = b8(1)
        assert one_value.value is True

        zero_value = b8(0)
        assert zero_value.value is False

        # Test with other truthy/falsy values
        empty_list = b8([])
        assert empty_list.value is False

        non_empty_list = b8([1, 2, 3])
        assert non_empty_list.value is True

        # Test with another b8
        value2 = b8(true_value)
        assert value2.value is True

        # Test with strings
        empty_string = b8("")
        assert empty_string.value is False

        non_empty_string = b8("Hello")
        assert non_empty_string.value is True

    def test_bool_conversions(self):
        """Test conversion of boolean types to Python types."""
        # Test bool() conversion
        assert bool(b8(True)) is True
        assert bool(b8(False)) is False

        # Test str() conversion
        assert str(b8(True)) == "True"
        assert str(b8(False)) == "False"

        # Test repr() format
        assert repr(b8(True)) == "B8(True)"
        assert repr(b8(False)) == "B8(False)"

    def test_bool_comparisons(self):
        """Test comparison operations between boolean types."""
        # Test equality with same type
        assert b8(True) == b8(True)
        assert b8(False) == b8(False)
        assert b8(True) != b8(False)

        # Test equality with Python boolean
        assert b8(True) == True
        assert b8(False) == False
        assert b8(True) != False
        assert b8(False) != True

        # Test equality with non-boolean types
        assert b8(True) != 1
        assert b8(False) != 0
        assert b8(True) != "True"

    def test_rayobject_construction(self):
        """Test creating boolean types from RayObject instances."""
        # Create RayObject instances
        ray_true = r.RayObject.from_b8(True)
        ray_false = r.RayObject.from_b8(False)

        # Create boolean type from RayObject
        value_true = b8(False, ray_obj=ray_true)
        value_false = b8(True, ray_obj=ray_false)

        # Verify values and types
        assert value_true.value is True
        assert value_false.value is False
        assert value_true.ptr.get_type() == -r.TYPE_B8
        assert value_false.ptr.get_type() == -r.TYPE_B8

        # Test with wrong RayObject type
        ray_i64 = r.RayObject.from_i64(42)
        with pytest.raises(ValueError):
            b8(False, ray_obj=ray_i64)

    def test_logical_operations(self):
        """Test that boolean values work with Python logical operations."""
        # We can't test actual logical operations with Rayforce objects directly,
        # but we can test using their Python boolean values

        true_val = b8(True)
        false_val = b8(False)

        # Test logical operations
        assert true_val.value and True
        assert not (false_val.value and True)
        assert true_val.value or False
        assert not (false_val.value and False)

        # Проверим операцию NOT
        assert not false_val.value
        assert not false_val.value is True

        # Проверим комбинированные операции
        assert (true_val.value or false_val.value) is True
        assert (true_val.value and false_val.value) is False

        # Test in conditional expressions
        result = "yes" if true_val.value else "no"
        assert result == "yes"

        result = "yes" if false_val.value else "no"
        assert result == "no"
