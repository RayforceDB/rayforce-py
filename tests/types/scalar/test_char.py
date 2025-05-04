import pytest

from raypy import _rayforce as r
from raypy.types.scalar.char import c8


class TestCharType:
    def test_c8_creation_from_string(self):
        """Test creating a c8 from a string character."""
        # Test with standard ASCII character
        char_obj = c8("A")
        assert char_obj.value == "A"

        # Test with non-ASCII character (should be converted to "A")
        char_obj = c8("é")
        assert char_obj.value == "A"

        # Test with string that's too long
        with pytest.raises(ValueError):
            c8("AB")  # Too many characters

        # Test with empty string
        with pytest.raises(ValueError):
            c8("")  # Not enough characters

    def test_c8_creation_from_int(self):
        """Test creating a c8 from an integer code point."""
        # Test with valid ASCII integer
        char_obj = c8(65)  # ASCII for 'A'
        assert char_obj.value == "A"

        # Test with valid integer at boundary
        char_obj = c8(0)
        assert char_obj.value == "\x00"

        # Test with highest valid ASCII (126 is '~')
        char_obj = c8(126)
        assert char_obj.value == "~"

        # Test with integer value 127 (which is not valid for c8 according to implementation)
        with pytest.raises(ValueError):
            c8(127)

        # Test with out-of-range integers
        with pytest.raises(ValueError):
            c8(-1)  # Too small

        with pytest.raises(ValueError):
            c8(256)  # Too large

    def test_c8_invalid_creation(self):
        """Test that creating a c8 with invalid types raises errors."""
        with pytest.raises(ValueError):
            c8([])  # List is not a valid input

        with pytest.raises(ValueError):
            c8({})  # Dict is not a valid input

        with pytest.raises(ValueError):
            c8(None)  # None is not a valid input

    def test_c8_properties(self):
        """Test c8 properties and methods."""
        char_obj = c8("A")

        # Test value property
        assert char_obj.value == "A"

        # Test code property
        assert char_obj.code == 65

        # Test string representation
        assert str(char_obj) == "A"

        # Test repr format
        assert repr(char_obj) == "c8(A)"

    def test_c8_equality(self):
        """Test equality comparisons with c8 objects."""
        char_a = c8("A")
        char_a2 = c8(65)  # Same as 'A'
        char_b = c8("B")

        # Test equality with another c8
        assert char_a == char_a2
        assert char_a != char_b

        # Test equality with string
        assert char_a == "A"
        assert char_a != "B"

        # Test equality with invalid types
        assert char_a != 65  # Integer is not equal even if it's the code point
        assert char_a != ["A"]  # List is not equal
        assert char_a != None  # None is not equal

        # Test equality with multi-character string
        assert char_a != "AA"

    def test_rayobject_construction(self):
        """Test creating c8 objects from RayObject instances."""
        # Create RayObject instance
        ray_char = r.RayObject.from_c8("A")

        # Create c8 from RayObject
        char_obj = c8("B", ray_obj=ray_char)

        # Verify values and types
        assert char_obj.value == "A"  # Value should come from ray_obj, not from "B"
        assert char_obj.ptr.get_type() == -r.TYPE_C8

        # Test with wrong RayObject type
        ray_i64 = r.RayObject.from_i64(65)
        with pytest.raises(ValueError):
            c8("A", ray_obj=ray_i64)
