import pytest
import uuid

from raypy import _rayforce as r
from raypy.types.scalar.guid import GUID


class TestGUIDType:
    def test_guid_creation_empty(self):
        """Test creating a GUID without parameters (generates random UUID)."""
        guid_obj = GUID()

        # Check that result is a valid UUID
        assert isinstance(guid_obj.value, uuid.UUID)
        assert guid_obj.ptr.get_type() == r.TYPE_GUID

        # Creating another empty GUID should generate a different UUID
        another_guid = GUID()
        assert guid_obj.value != another_guid.value

    def test_guid_creation_from_string(self):
        """Test creating a GUID from a string."""
        # Test with valid UUID string
        test_uuid_str = "f81d4fae-7dec-11d0-a765-00a0c91e6bf6"
        guid_obj = GUID(test_uuid_str)

        assert str(guid_obj.value) == test_uuid_str
        assert guid_obj.value == uuid.UUID(test_uuid_str)

        # Test with invalid UUID string
        with pytest.raises(ValueError):
            GUID("not-a-valid-uuid")

    def test_guid_creation_from_uuid(self):
        """Test creating a GUID from a Python UUID object."""
        test_uuid = uuid.UUID("f81d4fae-7dec-11d0-a765-00a0c91e6bf6")
        guid_obj = GUID(test_uuid)

        assert guid_obj.value == test_uuid
        assert str(guid_obj) == str(test_uuid)

    def test_guid_creation_from_bytes(self):
        """Test creating a GUID from bytes."""
        # Create test UUID and get its bytes
        test_uuid = uuid.UUID("f81d4fae-7dec-11d0-a765-00a0c91e6bf6")
        test_bytes = test_uuid.bytes

        # Create GUID from bytes
        guid_obj = GUID(test_bytes)

        assert guid_obj.value == test_uuid

        # Create GUID from bytearray
        guid_obj2 = GUID(bytearray(test_bytes))

        assert guid_obj2.value == test_uuid

        # Test with invalid bytes length
        with pytest.raises(ValueError):
            GUID(b"too_short")

    def test_guid_invalid_creation(self):
        """Test that creating a GUID with invalid types raises errors."""
        with pytest.raises(TypeError):
            GUID(123)  # Integer is not a valid input

        with pytest.raises(TypeError):
            GUID([1, 2, 3])  # List is not a valid input

        with pytest.raises(TypeError):
            GUID({"key": "value"})  # Dict is not a valid input

    def test_guid_properties(self):
        """Test GUID properties and methods."""
        test_uuid_str = "f81d4fae-7dec-11d0-a765-00a0c91e6bf6"
        test_uuid = uuid.UUID(test_uuid_str)
        guid_obj = GUID(test_uuid)

        # Test value property
        assert guid_obj.value == test_uuid

        # Test hex property
        assert guid_obj.hex == test_uuid.hex

        # Test urn property
        assert guid_obj.urn == f"urn:uuid:{test_uuid_str}"

        # Test string representation
        assert str(guid_obj) == test_uuid_str

        # Test repr format
        assert repr(guid_obj) == f"GUID({test_uuid_str})"

    def test_guid_equality(self):
        """Test equality comparisons with GUID objects."""
        test_uuid_str = "f81d4fae-7dec-11d0-a765-00a0c91e6bf6"
        test_uuid = uuid.UUID(test_uuid_str)
        guid_obj1 = GUID(test_uuid)
        guid_obj2 = GUID(test_uuid_str)

        # Test equality with another GUID
        assert guid_obj1 == guid_obj2

        # Test equality with Python UUID
        assert guid_obj1 == test_uuid

        # Test equality with UUID string
        assert guid_obj1 == test_uuid_str

        # Test equality with raw bytes
        assert guid_obj1 == test_uuid.bytes

        # Test inequality
        different_uuid = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        assert guid_obj1 != GUID(different_uuid)
        assert guid_obj1 != different_uuid
        assert guid_obj1 != str(different_uuid)
        assert guid_obj1 != different_uuid.bytes

        # Test equality with invalid types
        assert guid_obj1 != 123
        assert guid_obj1 != "not-a-valid-uuid"
        assert guid_obj1 != b"too_short"

    def test_rayobject_construction(self):
        """Test creating GUID objects from RayObject instances."""
        # Create a UUID and get its bytes
        test_uuid = uuid.UUID("f81d4fae-7dec-11d0-a765-00a0c91e6bf6")
        test_bytes = test_uuid.bytes

        # Create RayObject instance
        ray_guid = r.RayObject.from_guid(test_bytes)

        # Create GUID from RayObject
        guid_obj = GUID(ray_obj=ray_guid)

        # Verify values and types
        assert guid_obj.value == test_uuid
        assert guid_obj.ptr.get_type() == r.TYPE_GUID

        # Test with wrong RayObject type
        ray_i64 = r.RayObject.from_i64(42)
        with pytest.raises(ValueError):
            GUID(ray_obj=ray_i64)
