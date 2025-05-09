import pytest
import datetime as dt

from raypy import _rayforce as r
from raypy.types.scalar.time import Time


class TestTimeType:
    def test_time_creation_empty(self):
        """Test creating a Time without parameters (defaults to current time)."""
        # Since current time changes during test execution, we can only
        # test that the result is a time object and has expected type
        time_obj = Time()

        assert isinstance(time_obj.value, dt.time)
        assert time_obj.ptr.get_type() == -r.TYPE_TIME

    def test_time_creation_from_time(self):
        """Test creating a Time from a Python time object."""
        # Test with specific time
        test_time = dt.time(12, 34, 56, 789000)  # With microseconds
        time_obj = Time(test_time)

        assert time_obj.value.hour == 12
        assert time_obj.value.minute == 34
        assert time_obj.value.second == 56
        assert time_obj.value.microsecond == 789000

        # Calculate raw value (milliseconds since midnight)
        expected_ms = (12 * 3600 + 34 * 60 + 56) * 1000 + 789
        assert time_obj.ms_since_midnight == expected_ms

        # Test with midnight
        midnight = dt.time(0, 0, 0)
        midnight_obj = Time(midnight)
        assert midnight_obj.value == midnight
        assert midnight_obj.ms_since_midnight == 0

    def test_time_creation_from_int(self):
        """Test creating a Time from an integer (milliseconds since midnight)."""
        # Test with specific milliseconds value
        ms = 45296789  # 12:34:56.789
        time_obj = Time(ms)

        expected_time = dt.time(12, 34, 56, 789000)
        assert time_obj.value == expected_time
        assert time_obj.ms_since_midnight == ms

        # Test with zero (midnight)
        midnight_obj = Time(0)
        assert midnight_obj.value == dt.time(0, 0, 0)
        assert midnight_obj.ms_since_midnight == 0

        # Test with max value (23:59:59.999)
        max_ms = 86399999
        max_obj = Time(max_ms)
        assert max_obj.value == dt.time(23, 59, 59, 999000)
        assert max_obj.ms_since_midnight == max_ms

        # Test invalid values
        with pytest.raises(ValueError):
            Time(-1)  # Negative time

        with pytest.raises(ValueError):
            Time(86400000)  # Too large (24:00:00.000)

    def test_time_creation_from_str(self):
        """Test creating a Time from a string in ISO format."""
        # Test with valid ISO format without milliseconds
        time_str = "12:34:56"
        time_obj = Time(time_str)
        expected_time = dt.time(12, 34, 56)

        assert time_obj.value == expected_time

        # Test with valid ISO format with milliseconds
        time_str_ms = "12:34:56.789"
        time_obj_ms = Time(time_str_ms)
        expected_time_ms = dt.time(12, 34, 56, 789000)

        assert time_obj_ms.value == expected_time_ms

        # Test with invalid format
        with pytest.raises(ValueError):
            Time("12-34-56")  # Not ISO format

        with pytest.raises(ValueError):
            Time("not a time")

    def test_invalid_time_creation(self):
        """Test that creating a Time with invalid types raises errors."""
        with pytest.raises(TypeError):
            Time([])  # List is not a valid input

        with pytest.raises(TypeError):
            Time({})  # Dict is not a valid input

        with pytest.raises(TypeError):
            Time(1.5)  # Float is not a valid input

    def test_time_string_representation(self):
        """Test string representations of Time objects."""
        test_time = dt.time(12, 34, 56, 789000)
        time_obj = Time(test_time)

        # Test __str__
        assert str(time_obj) == "12:34:56.789"

        # Test __repr__
        assert repr(time_obj) == "Time(12:34:56.789)"

    def test_time_equality(self):
        """Test equality comparisons with Time objects."""
        test_time = dt.time(12, 34, 56, 789000)
        time_obj1 = Time(test_time)
        time_obj2 = Time(test_time)

        # Test equality with another Time
        assert time_obj1 == time_obj2

        # Test equality with Python time
        assert time_obj1 == test_time

        # Test equality with integer (ms since midnight)
        ms_since_midnight = (12 * 3600 + 34 * 60 + 56) * 1000 + 789
        assert time_obj1 == ms_since_midnight

        # Test inequality
        another_time = dt.time(10, 20, 30)
        assert time_obj1 != Time(another_time)
        assert time_obj1 != another_time
        assert time_obj1 != (10 * 3600 + 20 * 60 + 30) * 1000

        # Test equality with invalid types
        assert time_obj1 != "12:34:56.789"  # String comparison should return False
        assert time_obj1 != 123.45  # Float comparison should return False
        assert time_obj1 != [12, 34, 56]  # List comparison should return False

    def test_rayobject_construction(self):
        """Test creating Time objects from RayObject instances."""
        # Create RayObject instance
        ms_since_midnight = 45296789  # 12:34:56.789
        ray_time = r.RayObject.from_time(ms_since_midnight)

        # Create Time from RayObject
        time_obj = Time(ray_obj=ray_time)

        # Verify values and types
        expected_time = dt.time(12, 34, 56, 789000)
        assert time_obj.value == expected_time
        assert time_obj.ms_since_midnight == ms_since_midnight
        assert time_obj.ptr.get_type() == -r.TYPE_TIME

        # Test with wrong RayObject type
        ray_i64 = r.RayObject.from_i64(42)
        with pytest.raises(ValueError):
            Time(ray_obj=ray_i64)

    def test_time_properties(self):
        """Test time properties and methods."""
        test_time = dt.time(12, 34, 56, 789000)
        time_obj = Time(test_time)

        # Test basic time properties through the Python time object
        assert time_obj.value.hour == 12
        assert time_obj.value.minute == 34
        assert time_obj.value.second == 56
        assert time_obj.value.microsecond == 789000

        # Test raw_value (ms since midnight)
        expected_ms = (12 * 3600 + 34 * 60 + 56) * 1000 + 789
        assert time_obj.ms_since_midnight == expected_ms
