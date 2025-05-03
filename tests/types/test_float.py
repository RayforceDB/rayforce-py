import pytest
import math

from raypy import _rayforce as r
from raypy.types.float import f64, from_python_float


class TestFloatTypes:
    def test_f64_creation(self):
        # Test with regular float
        value = f64(42.5)
        assert value.value == 42.5
        assert type(value.value) == float
        assert value.ptr.get_type() == -r.TYPE_F64

        # Test with integer (should be converted to float)
        value_int = f64(42)
        assert value_int.value == 42.0
        assert isinstance(value_int.value, float)

        # Test with another f64
        value2 = f64(value)
        assert value2.value == 42.5

        # Test with special values
        inf_value = f64(float("inf"))
        assert math.isinf(inf_value.value)

        nan_value = f64(float("nan"))
        assert math.isnan(nan_value.value)

        # Test with very small and very large values
        small = f64(1e-308)
        assert small.value == 1e-308

        large = f64(1e308)
        assert large.value == 1e308

        # Test invalid values
        with pytest.raises(ValueError):
            f64("not a float")

    def test_from_python_float(self):
        # Test basic conversion
        value = from_python_float(42.5)
        assert isinstance(value, f64)
        assert value.value == 42.5

        # Test with forced type
        forced_f64 = from_python_float(42.5, force_type="f64")
        assert isinstance(forced_f64, f64)
        assert forced_f64.value == 42.5

        # Test invalid force_type
        with pytest.raises(ValueError):
            from_python_float(42.5, force_type="invalid")

    def test_float_conversions(self):
        # Test float() conversion
        assert float(f64(42.5)) == 42.5

        # Test str() conversion
        assert str(f64(42.5)) == "42.5"

        # Test repr() format
        assert repr(f64(42.5)) == "f64(42.5)"

    def test_float_comparisons(self):
        # Test equality with same type
        assert f64(42.5) == f64(42.5)

        # Test equality with Python float
        assert f64(42.5) == 42.5

        # Test inequality
        assert f64(42.5) != f64(43.5)
        assert f64(42.5) != 43.5

        # Test NaN comparison (NaN is not equal to anything, including itself)
        nan_value = f64(float("nan"))
        assert nan_value != nan_value
        assert nan_value != f64(float("nan"))

    def test_rayobject_construction(self):
        """Test creating float types from RayObject instances."""
        # Create RayObject instance
        ray_f64 = r.RayObject.from_f64(42.5)

        # Create float type from RayObject
        value_f64 = f64(0.0, ray_obj=ray_f64)

        # Verify values and types
        assert value_f64.value == 42.5
        assert value_f64.ptr.get_type() == -r.TYPE_F64

        # Test with wrong RayObject type
        ray_i64 = r.RayObject.from_i64(42)
        with pytest.raises(ValueError):
            f64(0.0, ray_obj=ray_i64)

    def test_float_arithmetic_compatibility(self):
        """Test that Rayforce floats work with Python arithmetic."""
        # We can't test actual arithmetic with Rayforce objects,
        # but we can test that conversion to Python float works properly
        # for use in arithmetic operations

        f = f64(42.5)

        # Test using a Rayforce float in Python arithmetic
        result = f.value + 7.5
        assert result == 50.0

        result = f.value * 2
        assert result == 85.0

        result = f.value / 2
        assert result == 21.25
