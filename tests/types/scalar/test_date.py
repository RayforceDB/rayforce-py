import pytest
import datetime as dt

from raypy import _rayforce as r
from raypy.types.scalar.date import Date, EPOCH_DATE


class TestDateType:
    def test_date_creation_empty(self):
        """Test creating a Date without parameters (defaults to today)."""
        today = dt.date.today()
        date_obj = Date()

        assert isinstance(date_obj.value, dt.date)
        assert date_obj.value == today
        assert date_obj.ptr.get_type() == -r.TYPE_DATE

    def test_date_creation_from_date(self):
        """Test creating a Date from a Python date object."""
        # Test with specific date
        test_date = dt.date(2023, 5, 15)
        date_obj = Date(test_date)

        assert date_obj.value == test_date
        assert date_obj.raw_value == (test_date - EPOCH_DATE).days

        # Test with epoch date
        epoch_date_obj = Date(EPOCH_DATE)
        assert epoch_date_obj.value == EPOCH_DATE
        assert epoch_date_obj.raw_value == 0

    def test_date_creation_from_int(self):
        """Test creating a Date from an integer (days since epoch)."""
        # Test with positive days
        days = 1000
        date_obj = Date(days)
        expected_date = EPOCH_DATE + dt.timedelta(days=days)

        assert date_obj.value == expected_date
        assert date_obj.raw_value == days

        # Test with zero (epoch)
        epoch_date_obj = Date(0)
        assert epoch_date_obj.value == EPOCH_DATE
        assert epoch_date_obj.raw_value == 0

        # Test with negative days (before epoch)
        neg_days = -1000
        neg_date_obj = Date(neg_days)
        expected_neg_date = EPOCH_DATE + dt.timedelta(days=neg_days)

        assert neg_date_obj.value == expected_neg_date
        assert neg_date_obj.raw_value == neg_days

    def test_date_creation_from_str(self):
        """Test creating a Date from a string in ISO format."""
        # Test with valid ISO format
        date_str = "2023-05-15"
        date_obj = Date(date_str)
        expected_date = dt.date(2023, 5, 15)

        assert date_obj.value == expected_date

        # Test with invalid format
        with pytest.raises(ValueError):
            Date("15-05-2023")  # Not ISO format

        with pytest.raises(ValueError):
            Date("not a date")

    def test_invalid_date_creation(self):
        """Test that creating a Date with invalid types raises errors."""
        with pytest.raises(TypeError):
            Date([])  # List is not a valid input

        with pytest.raises(TypeError):
            Date({})  # Dict is not a valid input

        with pytest.raises(TypeError):
            Date(1.5)  # Float is not a valid input

    def test_date_string_representation(self):
        """Test string representations of Date objects."""
        test_date = dt.date(2023, 5, 15)
        date_obj = Date(test_date)

        # Test __str__
        assert str(date_obj) == "2023-05-15"

        # Test __repr__
        assert repr(date_obj) == "Date(2023-05-15)"

    def test_date_equality(self):
        """Test equality comparisons with Date objects."""
        test_date = dt.date(2023, 5, 15)
        date_obj1 = Date(test_date)
        date_obj2 = Date(test_date)

        # Test equality with another Date
        assert date_obj1 == date_obj2

        # Test equality with Python date
        assert date_obj1 == test_date

        # Test equality with integer (days since epoch)
        days_since_epoch = (test_date - EPOCH_DATE).days
        assert date_obj1 == days_since_epoch

        # Test inequality
        another_date = dt.date(2022, 1, 1)
        assert date_obj1 != Date(another_date)
        assert date_obj1 != another_date
        assert date_obj1 != (another_date - EPOCH_DATE).days

        # Test equality with invalid types
        assert date_obj1 != "2023-05-15"  # String comparison should return False
        assert date_obj1 != 123.45  # Float comparison should return False
        assert date_obj1 != [2023, 5, 15]  # List comparison should return False

    def test_rayobject_construction(self):
        """Test creating Date objects from RayObject instances."""
        # Create RayObject instance
        days_since_epoch = 1000
        ray_date = r.RayObject.from_date(days_since_epoch)

        # Create Date from RayObject
        date_obj = Date(ray_obj=ray_date)

        # Verify values and types
        expected_date = EPOCH_DATE + dt.timedelta(days=days_since_epoch)
        assert date_obj.value == expected_date
        assert date_obj.raw_value == days_since_epoch
        assert date_obj.ptr.get_type() == -r.TYPE_DATE

        # Test with wrong RayObject type
        ray_i64 = r.RayObject.from_i64(42)
        with pytest.raises(ValueError):
            Date(ray_obj=ray_i64)

    def test_date_properties(self):
        """Test date properties and methods."""
        test_date = dt.date(2023, 5, 15)
        date_obj = Date(test_date)

        # Test basic date properties through the Python date object
        assert date_obj.value.year == 2023
        assert date_obj.value.month == 5
        assert date_obj.value.day == 15

        # Test raw_value (days since epoch)
        expected_days = (test_date - EPOCH_DATE).days
        assert date_obj.raw_value == expected_days
