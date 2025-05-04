import pytest

from raypy import _rayforce as r
from raypy.types.scalar.symbol import Symbol


class TestSymbolType:
    def test_symbol_creation_from_string(self):
        """Test creating a Symbol from a string."""
        # Test with simple string
        symbol_obj = Symbol("test")
        assert symbol_obj.value == "test"

        # Test with empty string
        symbol_obj = Symbol("")
        assert symbol_obj.value == ""

        # Test with special characters
        symbol_obj = Symbol("test-123_!@#")
        assert symbol_obj.value == "test-123_!@#"

        # Test with long string
        long_str = "a" * 1000
        symbol_obj = Symbol(long_str)
        assert symbol_obj.value == long_str

    def test_symbol_creation_from_non_string(self):
        """Test creating a Symbol from non-string types (auto-conversion)."""
        # Test with integer
        symbol_obj = Symbol(123)
        assert symbol_obj.value == "123"

        # Test with float
        symbol_obj = Symbol(3.14)
        assert symbol_obj.value == "3.14"

        # Test with boolean
        symbol_obj = Symbol(True)
        assert symbol_obj.value == "True"

    def test_symbol_properties(self):
        """Test Symbol properties and methods."""
        symbol_obj = Symbol("test_symbol")

        # Test value property
        assert symbol_obj.value == "test_symbol"

        # Test string representation
        assert str(symbol_obj) == "test_symbol"

        # Test repr format
        assert repr(symbol_obj) == "Symbol(test_symbol)"

    def test_symbol_equality(self):
        """Test equality comparisons with Symbol objects."""
        symbol1 = Symbol("test")
        symbol2 = Symbol("test")
        symbol3 = Symbol("other")

        # Test equality with another Symbol
        assert symbol1 == symbol2
        assert symbol1 != symbol3

        # Test equality with string
        assert symbol1 == "test"
        assert symbol1 != "other"

        # Test equality with non-string types
        assert symbol1 != 123
        assert symbol1 != True
        assert symbol1 != ["test"]
        assert symbol1 != None

    def test_rayobject_construction(self):
        """Test creating Symbol objects from RayObject instances."""
        # Create RayObject instance
        ray_symbol = r.RayObject.from_symbol("test_ray")

        # Create Symbol from RayObject
        symbol_obj = Symbol("ignored", ray_obj=ray_symbol)

        # Verify values and types
        assert (
            symbol_obj.value == "test_ray"
        )  # Value should come from ray_obj, not from "ignored"
        assert symbol_obj.ptr.get_type() == -r.TYPE_SYMBOL

        # Test with wrong RayObject type
        ray_i64 = r.RayObject.from_i64(42)
        with pytest.raises(ValueError):
            Symbol("test", ray_obj=ray_i64)

    def test_init_error_handling(self):
        """Test initialization error handling in Symbol."""
        # Test with modifying the RayObject method to trigger an exception
        orig_method = Symbol.ray_init_method
        try:
            Symbol.ray_init_method = "nonexistent_method"
            with pytest.raises(TypeError):
                Symbol("test")
        finally:
            Symbol.ray_init_method = orig_method
