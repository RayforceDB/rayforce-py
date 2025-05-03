import pytest

from raypy import _rayforce as r
from raypy.types.integer import i16, i32, i64, from_python_integer


class TestIntegerTypes:
    def test_i16_creation(self):
        # Test with regular integer
        value = i16(42)
        assert value.value == 42
        assert type(value.value) == int
        assert value.ptr.get_type() == -r.TYPE_I16

        # Test with floating point (should be truncated)
        value_float = i16(42.9)
        assert value_float.value == 42

        # Test with another i16
        value2 = i16(value)
        assert value2.value == 42

        # Test limits
        max_i16 = i16(32767)
        assert max_i16.value == 32767

        min_i16 = i16(-32768)
        assert min_i16.value == -32768

        # Test invalid values
        with pytest.raises(TypeError):
            i16(32768)  # Too large

        with pytest.raises(TypeError):
            i16(-32769)  # Too small

        with pytest.raises(ValueError):
            i16("not an integer")

    def test_i32_creation(self):
        # Test with regular integer
        value = i32(42)
        assert value.value == 42
        assert type(value.value) == int
        assert value.ptr.get_type() == -r.TYPE_I32

        # Test with floating point (should be truncated)
        value_float = i32(42.9)
        assert value_float.value == 42

        # Test with another i32
        value2 = i32(value)
        assert value2.value == 42

        # Test limits
        max_i32 = i32(2147483647)
        assert max_i32.value == 2147483647

        min_i32 = i32(-2147483648)
        assert min_i32.value == -2147483648

        # Test invalid values
        with pytest.raises(TypeError):
            i32(2147483648)  # Too large

        with pytest.raises(TypeError):
            i32(-2147483649)  # Too small

        with pytest.raises(ValueError):
            i32("not an integer")

    def test_i64_creation(self):
        """Test creation of i64 integers with different inputs."""
        # Test with regular integer
        value = i64(42)
        assert value.value == 42
        assert type(value.value) == int
        assert value.ptr.get_type() == -r.TYPE_I64

        # Test with floating point (should be truncated)
        value_float = i64(42.9)
        assert value_float.value == 42

        # Test with another i64
        value2 = i64(value)
        assert value2.value == 42

        # Test large values
        large = i64(9223372036854775807)  # Max for signed 64-bit int
        assert large.value == 9223372036854775807

        # Test invalid values
        with pytest.raises(ValueError):
            i64("not an integer")

    def test_from_python_integer(self):
        """Test automatic selection of integer type based on value."""
        # Small value should be i16
        small = from_python_integer(100)
        assert isinstance(small, i16)
        assert small.value == 100

        # Medium value should be i32
        medium = from_python_integer(100000)
        assert isinstance(medium, i32)
        assert medium.value == 100000

        # Large value should be i64
        large = from_python_integer(10000000000)
        assert isinstance(large, i64)
        assert large.value == 10000000000

        # Test forced types
        forced_i16 = from_python_integer(1000, force_type="i16")
        assert isinstance(forced_i16, i16)

        forced_i32 = from_python_integer(100000, force_type="i32")
        assert isinstance(forced_i32, i32)

        forced_i64 = from_python_integer(100, force_type="i64")
        assert isinstance(forced_i64, i64)

        # Test invalid force_type
        with pytest.raises(ValueError):
            from_python_integer(100, force_type="invalid")

    def test_integer_conversions(self):
        """Test conversion of integer types to Python types."""
        # Test int() conversion
        assert int(i16(42)) == 42
        assert int(i32(42)) == 42
        assert int(i64(42)) == 42

        # Test str() conversion
        assert str(i16(42)) == "42"
        assert str(i32(42)) == "42"
        assert str(i64(42)) == "42"

        # Test repr() format
        assert repr(i16(42)) == "i16(42)"
        assert repr(i32(42)) == "i32(42)"
        assert repr(i64(42)) == "i64(42)"

    def test_integer_comparisons(self):
        """Test comparison operations between integer types."""
        # Test equality between same types
        assert i16(42) == i16(42)
        assert i32(42) == i32(42)
        assert i64(42) == i64(42)

        # Test equality between different types
        assert i16(42) == i32(42)
        assert i16(42) == i64(42)
        assert i32(42) == i64(42)

        # Test equality with Python integers
        assert i16(42) == 42
        assert i32(42) == 42
        assert i64(42) == 42

        # Test inequality
        assert i16(42) != i16(43)
        assert i16(42) != i32(43)
        assert i16(42) != 43

    def test_rayobject_construction(self):
        """Test creating integer types from RayObject instances."""
        # Create RayObject instances
        ray_i16 = r.RayObject.from_i16(42)
        ray_i32 = r.RayObject.from_i32(42)
        ray_i64 = r.RayObject.from_i64(42)

        # Create integer types from RayObjects
        value_i16 = i16(0, ray_obj=ray_i16)
        value_i32 = i32(0, ray_obj=ray_i32)
        value_i64 = i64(0, ray_obj=ray_i64)

        # Verify values and types
        assert value_i16.value == 42
        assert value_i32.value == 42
        assert value_i64.value == 42

        assert value_i16.ptr.get_type() == -r.TYPE_I16
        assert value_i32.ptr.get_type() == -r.TYPE_I32
        assert value_i64.ptr.get_type() == -r.TYPE_I64

        # Test with wrong RayObject types
        with pytest.raises(ValueError):
            i16(0, ray_obj=ray_i32)
        with pytest.raises(ValueError):
            i32(0, ray_obj=ray_i64)
        with pytest.raises(ValueError):
            i64(0, ray_obj=ray_i16)
