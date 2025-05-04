import pytest

from raypy import _rayforce as r
from raypy.types.container import List
from raypy.types.scalar import Symbol, i64, b8


class TestListContainer:
    def test_list_creation(self):
        """Test creation of List with different inputs."""
        # Test empty list
        empty_list = List([])
        assert len(empty_list) == 0
        assert str(empty_list) == "[]"
        
        # Test list with simple integers
        int_list = List([1, 2, 3])
        assert len(int_list) == 3
        assert int_list[0] == 1
        assert int_list[1] == 2
        assert int_list[2] == 3
        
        # Test list with mixed types
        mixed_list = List([1, "test", True])
        assert len(mixed_list) == 3
        assert mixed_list[0] == 1
        assert mixed_list[1] == "test"
        assert mixed_list[2] == True
        
        # Test creation with None should raise error
        with pytest.raises(ValueError):
            List(None)
            
        # Test with non-iterable should raise error
        with pytest.raises(ValueError):
            List(123)
    
    def test_list_from_rayobject(self):
        """Test creating List from RayObject instances."""
        # Create a list using the RayObject API
        ray_list = r.RayObject.create_list()
        ray_list.list_append(r.RayObject.from_i64(10))
        ray_list.list_append(r.RayObject.from_i64(20))
        
        # Create a List from the RayObject
        list_obj = List(ray_obj=ray_list)
        
        # Verify values and types
        assert len(list_obj) == 2
        assert list_obj[0] == 10
        assert list_obj[1] == 20
        
        # Test with wrong RayObject type
        ray_i64 = r.RayObject.from_i64(42)
        with pytest.raises(ValueError):
            List(ray_obj=ray_i64)
    
    def test_list_append(self):
        """Test append method of List."""
        my_list = List([])
        
        # Append various types
        my_list.append(10)  # int
        my_list.append("test")  # str
        my_list.append(True)  # bool
        my_list.append(i64(42))  # raypy type
        
        # Verify
        assert len(my_list) == 4
        assert my_list[0] == 10
        assert my_list[1] == "test"
        assert my_list[2] == True
        assert my_list[3] == 42
        
        # Append a raw RayObject
        ray_obj = r.RayObject.from_i64(100)
        my_list.append(ray_obj)
        assert my_list[4] == 100
    
    def test_list_get_and_indexing(self):
        """Test get method and indexing operation."""
        my_list = List([10, 20, 30])
        
        # Test get method
        assert my_list.get(0) == 10
        assert my_list.get(1) == 20
        assert my_list.get(2) == 30
        
        # Test get with invalid index
        with pytest.raises(IndexError):
            my_list.get(-1)
            
        with pytest.raises(IndexError):
            my_list.get(3)
        
        # Test indexing operator
        assert my_list[0] == 10
        assert my_list[1] == 20
        assert my_list[2] == 30
        
        # Test indexing with invalid index
        with pytest.raises(IndexError):
            value = my_list[-1]
            
        with pytest.raises(IndexError):
            value = my_list[3]
    
    def test_list_set_and_assignment(self):
        """Test set method and assignment operation."""
        my_list = List([10, 20, 30])
        
        # Test set method
        my_list.set(0, 100)
        assert my_list[0] == 100
        
        # Test set with raypy type
        my_list.set(1, i64(200))
        assert my_list[1] == 200
        
        # Test set with raw RayObject
        ray_obj = r.RayObject.from_i64(300)
        my_list.set(2, ray_obj)
        assert my_list[2] == 300
        
        # Test set with invalid index
        with pytest.raises(IndexError):
            my_list.set(-1, 400)
            
        with pytest.raises(IndexError):
            my_list.set(3, 400)
        
        # Test assignment operator
        my_list[0] = 1000
        assert my_list[0] == 1000
        
        # Test assignment with raypy type
        my_list[1] = b8(False)
        assert my_list[1] == False
        
        # Test assignment with invalid index
        with pytest.raises(IndexError):
            my_list[-1] = 4000
            
        with pytest.raises(IndexError):
            my_list[3] = 4000
    
    def test_list_remove(self):
        """Test remove method of List."""
        my_list = List([10, 20, 30, 40])
        
        # Remove an item
        my_list.remove(1)  # Remove 20
        assert len(my_list) == 3
        assert my_list[0] == 10
        assert my_list[1] == 30
        assert my_list[2] == 40
        
        # Remove another item
        my_list.remove(0)  # Remove 10
        assert len(my_list) == 2
        assert my_list[0] == 30
        assert my_list[1] == 40
        
        # Test remove with invalid index
        with pytest.raises(IndexError):
            my_list.remove(-1)
            
        with pytest.raises(IndexError):
            my_list.remove(2)
    
    def test_list_iteration(self):
        """Test iteration over List items."""
        my_list = List([10, 20, 30])
        
        # Use in a for loop
        items = []
        for item in my_list:
            items.append(item)
        
        assert items == [10, 20, 30]
        
        # Use with list comprehension
        items = [item for item in my_list]
        assert items == [10, 20, 30]
    
    def test_list_string_representation(self):
        """Test string and representation methods."""
        my_list = List([10, 20, 30])
        
        # Test __str__
        assert str(my_list) == "[i64(10), i64(20), i64(30)]"
        
        # Test __repr__
        assert repr(my_list) == "List([i64(10), i64(20), i64(30)])"
        
        # Test with mixed types
        mixed_list = List([10, "test", True])
        assert str(mixed_list) == "[i64(10), Symbol(test), b8(True)]"
        
        # Test empty list
        empty_list = List([])
        assert str(empty_list) == "[]"
        assert repr(empty_list) == "List([])"
    
    def test_list_nesting(self):
        """Test nesting lists within lists."""
        inner_list = List([1, 2, 3])
        outer_list = List([10, inner_list, 30])
        
        assert len(outer_list) == 3
        assert outer_list[0] == 10
        
        # Verify the inner list was correctly stored
        retrieved_inner = outer_list[1]
        assert isinstance(retrieved_inner, List)
        assert len(retrieved_inner) == 3
        assert retrieved_inner[0] == 1
        assert retrieved_inner[1] == 2
        assert retrieved_inner[2] == 3
        
        assert outer_list[2] == 30
    
    def test_list_with_raypy_types(self):
        """Test List with various raypy types."""
        # Create list with raypy types
        i64_val = i64(100)
        sym_val = Symbol("test")
        bool_val = b8(True)
        
        my_list = List([i64_val, sym_val, bool_val])
        
        # Verify values and types
        assert my_list[0] == 100
        assert my_list[1] == "test"
        assert my_list[2] == True
        
        # Complex example with mixed types
        complex_list = List([
            10,
            "string",
            True,
            i64(200),
            Symbol("symbol"),
            List([1, 2, 3])
        ])
        
        assert len(complex_list) == 6
        assert complex_list[0] == 10
        assert complex_list[1] == "string"
        assert complex_list[2] == True
        assert complex_list[3] == 200
        assert complex_list[4] == "symbol"
        
        nested = complex_list[5]
        assert isinstance(nested, List)
        assert len(nested) == 3
        assert nested[0] == 1
        assert nested[1] == 2
        assert nested[2] == 3
