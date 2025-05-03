import pytest

from raypy import _rayforce as r
from raypy.types.list import List
from raypy.types.symbol import Symbol
from raypy.types.integer import i64


class TestListType:
    def test_list_creation_empty(self):
        """Test creating an empty List."""
        list_obj = List()
        assert len(list_obj) == 0
        assert str(list_obj) == "[]"
        assert repr(list_obj) == "List([])"

    def test_list_creation_with_items(self):
        """Test creating a List with items."""
        # Create some RayObjects to use in the list
        ray_i64_1 = r.RayObject.from_i64(10)
        ray_i64_2 = r.RayObject.from_i64(20)
        ray_symbol = r.RayObject.from_symbol("test")

        # Create list with items
        list_obj = List([ray_i64_1, ray_i64_2, ray_symbol])

        # Check list properties
        assert len(list_obj) == 3

        # Verify individual items
        assert list_obj[0].get_i64_value() == 10
        assert list_obj[1].get_i64_value() == 20
        assert list_obj[2].get_symbol_value() == "test"

    def test_list_append(self):
        """Test append method."""
        list_obj = List()

        # Append some items
        ray_i64 = r.RayObject.from_i64(42)
        list_obj.append(ray_i64)
        assert len(list_obj) == 1

        ray_sym = r.RayObject.from_symbol("hello")
        list_obj.append(ray_sym)
        assert len(list_obj) == 2

        # Check values
        assert list_obj[0].get_i64_value() == 42
        assert list_obj[1].get_symbol_value() == "hello"

    def test_list_get_set(self):
        """Test get and set methods."""
        # Create a list with items
        ray_i64 = r.RayObject.from_i64(10)
        ray_sym = r.RayObject.from_symbol("test")
        list_obj = List([ray_i64, ray_sym])

        # Test get
        assert list_obj.get(0).get_i64_value() == 10
        assert list_obj.get(1).get_symbol_value() == "test"

        # Test set
        new_ray_i64 = r.RayObject.from_i64(99)
        list_obj.set(0, new_ray_i64)
        assert list_obj.get(0).get_i64_value() == 99

        # Test indexing syntax
        assert list_obj[1].get_symbol_value() == "test"
        list_obj[1] = r.RayObject.from_symbol("updated")
        assert list_obj[1].get_symbol_value() == "updated"

    def test_list_remove(self):
        """Test remove method."""
        # Create a list with items
        ray_items = [
            r.RayObject.from_i64(10),
            r.RayObject.from_i64(20),
            r.RayObject.from_i64(30),
        ]
        list_obj = List(ray_items)
        assert len(list_obj) == 3

        # Remove middle item
        list_obj.remove(1)
        assert len(list_obj) == 2
        assert list_obj[0].get_i64_value() == 10
        assert list_obj[1].get_i64_value() == 30

        # Remove first item
        list_obj.remove(0)
        assert len(list_obj) == 1
        assert list_obj[0].get_i64_value() == 30

        # Remove last item
        list_obj.remove(0)
        assert len(list_obj) == 0

    def test_list_iteration(self):
        """Test iterating over list."""
        # Create a list with items
        ray_items = [
            r.RayObject.from_i64(10),
            r.RayObject.from_i64(20),
            r.RayObject.from_symbol("test"),
        ]
        list_obj = List(ray_items)

        # Test iteration
        values = []
        for item in list_obj:
            if item.get_type() == -r.TYPE_I64:
                values.append(item.get_i64_value())
            else:
                values.append(item.get_symbol_value())

        assert values == [10, 20, "test"]

    def test_list_boundary_checks(self):
        """Test boundary checks for list operations."""
        list_obj = List()
        ray_i64 = r.RayObject.from_i64(42)

        # Test get with invalid index
        with pytest.raises(IndexError):
            list_obj.get(0)  # Empty list

        # Add an item and test boundaries
        list_obj.append(ray_i64)

        with pytest.raises(IndexError):
            list_obj.get(-1)  # Negative index

        with pytest.raises(IndexError):
            list_obj.get(1)  # Index too large

        # Test set with invalid index
        with pytest.raises(IndexError):
            list_obj.set(-1, ray_i64)

        with pytest.raises(IndexError):
            list_obj.set(1, ray_i64)

        # Test remove with invalid index
        with pytest.raises(IndexError):
            list_obj.remove(-1)

        with pytest.raises(IndexError):
            list_obj.remove(1)

    def test_list_with_raypy_objects(self):
        """Test list with raypy wrapper objects instead of raw RayObjects."""
        # Create a list directly with RayObjects
        ray_list = List()

        # Append raypy objects by extracting their underlying RayObjects
        ray_list.append(i64(10).ptr)
        ray_list.append(i64(20).ptr)
        ray_list.append(Symbol("test").ptr)

        # Verify contents
        assert len(ray_list) == 3

        # Extract and verify items correctly
        # Need to provide value and ray_obj
        first_value = ray_list[0].get_i64_value()
        second_value = ray_list[1].get_i64_value()
        third_value = ray_list[2].get_symbol_value()

        # Verify values directly
        assert first_value == 10
        assert second_value == 20
        assert third_value == "test"

        # Test creating wrapper objects with ray_obj
        assert i64(0, ray_obj=ray_list[0]).value == 10
        assert i64(0, ray_obj=ray_list[1]).value == 20
        assert Symbol("", ray_obj=ray_list[2]).value == "test"
