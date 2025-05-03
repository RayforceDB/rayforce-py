import pytest
import datetime as dt
import time

from raypy import _rayforce as r
from raypy.types.timestamp import Timestamp, from_python_timestamp, EPOCH_DATE
from raypy.types.date import Date
from raypy.types.time import Time


class TestTimestampType:
    def test_timestamp_creation_empty(self):
        """Test creating a Timestamp without parameters (defaults to current time)."""
        # Since current time changes during test execution, we can only
        # test that the result is a datetime object and has expected type
        timestamp_obj = Timestamp()
        
        assert isinstance(timestamp_obj.value, dt.datetime)
        assert timestamp_obj.ptr.get_type() == -r.TYPE_TIMESTAMP
        
    def test_timestamp_creation_from_datetime(self):
        """Test creating a Timestamp from a Python datetime object."""
        # Test with specific datetime
        test_dt = dt.datetime(2023, 5, 15, 12, 34, 56, 789000)
        timestamp_obj = Timestamp(test_dt)
        
        # Check datetime components
        assert timestamp_obj.value.year == 2023
        assert timestamp_obj.value.month == 5
        assert timestamp_obj.value.day == 15
        assert timestamp_obj.value.hour == 12
        assert timestamp_obj.value.minute == 34
        assert timestamp_obj.value.second == 56
        assert timestamp_obj.value.microsecond == 789000
        
        # Calculate raw value (milliseconds since epoch)
        expected_ms = int(test_dt.timestamp() * 1000)
        assert timestamp_obj.raw_value == expected_ms
        
        # Test with epoch
        # Note: We can't directly test for raw_value == 0 because of timezone
        # issues, so we check that the timestamp corresponds to epoch start
        epoch_dt = dt.datetime(1970, 1, 1, 0, 0, 0)
        epoch_obj = Timestamp(epoch_dt)
        
        # Calculate expected offset for timezone
        expected_epoch_ms = int(epoch_dt.timestamp() * 1000)
        assert epoch_obj.raw_value == expected_epoch_ms
    
    def test_timestamp_creation_from_int(self):
        """Test creating a Timestamp from an integer (milliseconds since epoch)."""
        # Test with specific milliseconds since epoch
        # 2023-05-15 12:34:56.789
        ms_since_epoch = 1684154096789
        timestamp_obj = Timestamp(ms_since_epoch)
        
        expected_dt = dt.datetime.fromtimestamp(ms_since_epoch / 1000)
        
        # Check only the components we care about, since timestamp conversion 
        # can be affected by timezone
        assert timestamp_obj.value.year == expected_dt.year
        assert timestamp_obj.value.month == expected_dt.month
        assert timestamp_obj.value.day == expected_dt.day
        assert timestamp_obj.value.hour == expected_dt.hour
        assert timestamp_obj.value.minute == expected_dt.minute
        assert timestamp_obj.value.second == expected_dt.second
        assert timestamp_obj.value.microsecond == 789000
        
        assert timestamp_obj.raw_value == ms_since_epoch
        
        # Test with zero (epoch)
        epoch_obj = Timestamp(0)
        
        # Don't check the specific hour, as it depends on the timezone
        # Instead, use the datetime.fromtimestamp method to calculate what 
        # time epoch (0) corresponds to in the local timezone
        local_epoch = dt.datetime.fromtimestamp(0)
        
        assert epoch_obj.value.year == local_epoch.year
        assert epoch_obj.value.month == local_epoch.month
        assert epoch_obj.value.day == local_epoch.day
        assert epoch_obj.value.hour == local_epoch.hour
        assert epoch_obj.value.minute == local_epoch.minute
        assert epoch_obj.value.second == local_epoch.second
        assert epoch_obj.value.microsecond == 0
        assert epoch_obj.raw_value == 0
    
    def test_timestamp_creation_from_str(self):
        """Test creating a Timestamp from a string in ISO format."""
        # Test with valid ISO format
        dt_str = "2023-05-15T12:34:56.789"
        timestamp_obj = Timestamp(dt_str)
        
        assert timestamp_obj.value.year == 2023
        assert timestamp_obj.value.month == 5
        assert timestamp_obj.value.day == 15
        assert timestamp_obj.value.hour == 12
        assert timestamp_obj.value.minute == 34
        assert timestamp_obj.value.second == 56
        assert timestamp_obj.value.microsecond == 789000
        
        # Test with invalid format
        with pytest.raises(ValueError):
            Timestamp("not a timestamp")
    
    def test_invalid_timestamp_creation(self):
        """Test that creating a Timestamp with invalid types raises errors."""
        with pytest.raises(TypeError):
            Timestamp([])  # List is not a valid input
            
        with pytest.raises(TypeError):
            Timestamp({})  # Dict is not a valid input
            
        with pytest.raises(TypeError):
            Timestamp(1.5)  # Float is not a valid input
    
    def test_from_python_timestamp(self):
        """Test the from_python_timestamp function."""
        # Test with explicit datetime
        test_dt = dt.datetime(2023, 5, 15, 12, 34, 56, 789000)
        timestamp_obj = from_python_timestamp(test_dt)
        
        assert timestamp_obj.value.year == test_dt.year
        assert timestamp_obj.value.month == test_dt.month
        assert timestamp_obj.value.day == test_dt.day
        assert timestamp_obj.value.hour == test_dt.hour
        assert timestamp_obj.value.minute == test_dt.minute
        assert timestamp_obj.value.second == test_dt.second
        assert timestamp_obj.value.microsecond == test_dt.microsecond
        
        # Test with forced type
        forced_timestamp_obj = from_python_timestamp(test_dt, force_type="Timestamp")
        
        assert forced_timestamp_obj.value.year == test_dt.year
        assert forced_timestamp_obj.value.month == test_dt.month
        assert forced_timestamp_obj.value.day == test_dt.day
        
        # Test with invalid force_type
        with pytest.raises(ValueError):
            from_python_timestamp(test_dt, force_type="invalid")
    
    def test_timestamp_string_representation(self):
        """Test string representations of Timestamp objects."""
        test_dt = dt.datetime(2023, 5, 15, 12, 34, 56, 789000)
        timestamp_obj = Timestamp(test_dt)
        
        # Test __str__
        assert str(timestamp_obj) == "2023-05-15T12:34:56.789"
        
        # Test __repr__
        assert repr(timestamp_obj) == "Timestamp(2023-05-15T12:34:56.789)"
    
    def test_timestamp_equality(self):
        """Test equality comparisons with Timestamp objects."""
        test_dt = dt.datetime(2023, 5, 15, 12, 34, 56, 789000)
        timestamp_obj1 = Timestamp(test_dt)
        timestamp_obj2 = Timestamp(test_dt)
        
        # Test equality with another Timestamp
        assert timestamp_obj1 == timestamp_obj2
        
        # Test equality with Python datetime
        assert timestamp_obj1 == test_dt
        
        # Test equality with integer (ms since epoch)
        ms_since_epoch = int(test_dt.timestamp() * 1000)
        assert timestamp_obj1 == ms_since_epoch
        
        # Test inequality
        another_dt = dt.datetime(2022, 1, 1, 10, 20, 30)
        assert timestamp_obj1 != Timestamp(another_dt)
        assert timestamp_obj1 != another_dt
        assert timestamp_obj1 != int(another_dt.timestamp() * 1000)
        
        # Test equality with invalid types
        assert timestamp_obj1 != "2023-05-15T12:34:56.789"  # String comparison should return False
        assert timestamp_obj1 != 123.45  # Float comparison should return False
        assert timestamp_obj1 != [2023, 5, 15]  # List comparison should return False
    
    def test_date_time_properties(self):
        """Test the date and time properties of Timestamp."""
        test_dt = dt.datetime(2023, 5, 15, 12, 34, 56, 789000)
        timestamp_obj = Timestamp(test_dt)
        
        # Test date property
        date_obj = timestamp_obj.date
        assert isinstance(date_obj, Date)
        assert date_obj.value.year == 2023
        assert date_obj.value.month == 5
        assert date_obj.value.day == 15
        
        # Test time property
        time_obj = timestamp_obj.time
        assert isinstance(time_obj, Time)
        assert time_obj.value.hour == 12
        assert time_obj.value.minute == 34
        assert time_obj.value.second == 56
        assert time_obj.value.microsecond == 789000
    
    def test_rayobject_construction(self):
        """Test creating Timestamp objects from RayObject instances."""
        # Create RayObject instance
        ms_since_epoch = 1684154096789  # 2023-05-15 12:34:56.789
        ray_timestamp = r.RayObject.from_timestamp(ms_since_epoch)
        
        # Create Timestamp from RayObject
        timestamp_obj = Timestamp(ray_obj=ray_timestamp)
        
        # Verify values and types
        expected_dt = dt.datetime.fromtimestamp(ms_since_epoch / 1000)
        assert timestamp_obj.value.year == expected_dt.year
        assert timestamp_obj.value.month == expected_dt.month
        assert timestamp_obj.value.day == expected_dt.day
        assert timestamp_obj.value.hour == expected_dt.hour
        assert timestamp_obj.value.minute == expected_dt.minute
        assert timestamp_obj.value.second == expected_dt.second
        assert timestamp_obj.value.microsecond == 789000
        
        assert timestamp_obj.raw_value == ms_since_epoch
        assert timestamp_obj.ptr.get_type() == -r.TYPE_TIMESTAMP
        
        # Test with wrong RayObject type
        ray_i64 = r.RayObject.from_i64(42)
        with pytest.raises(ValueError):
            Timestamp(ray_obj=ray_i64)
