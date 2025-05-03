import pytest

from raypy import _rayforce as r
from raypy.types.unsigned import u8


class TestUnsignedTypes:
    def test_u8_creation(self):
        """Test creation of u8 unsigned integers with different inputs."""
        # Test with regular integer
        value = u8(42)
        assert value.value == 42
        assert type(value.value) == int
        assert value.ptr.get_type() == -r.TYPE_U8
        
        # Test with string that can be converted to int
        str_value = u8("100")
        assert str_value.value == 100
        
        # Test with another u8
        value2 = u8(value)
        assert value2.value == 42
        
        # Test with boundary values
        min_u8 = u8(0)
        assert min_u8.value == 0
        
        max_u8 = u8(255)
        assert max_u8.value == 255
        
        # Test with invalid values
        with pytest.raises(ValueError):
            u8(256)  # Too large
            
        with pytest.raises(ValueError):
            u8(-1)  # Negative value
            
        with pytest.raises(ValueError):
            u8("not an integer")
    
    def test_u8_conversions(self):
        """Test conversion of u8 to Python types."""
        # Test int() conversion
        assert int(u8(42)) == 42
        
        # Test index() for use in slicing, etc.
        my_list = [0, 1, 2, 3, 4]
        index = u8(2)
        assert my_list[index] == 2
        
        # Test str() conversion
        assert str(u8(42)) == "42"
        
        # Test repr() format
        assert repr(u8(42)) == "u8(42)"
    
    def test_u8_comparisons(self):
        """Test comparison operations for u8."""
        # Test equality between same types
        assert u8(42) == u8(42)
        assert u8(42) != u8(43)
        
        # Test equality with Python integers
        assert u8(42) == 42
        assert u8(42) != 43
        
        # Test equality with other types
        assert u8(42) != "42"
        assert u8(42) != 42.0
    
    def test_rayobject_construction(self):
        """Test creating u8 from RayObject instances."""
        # Create RayObject instance
        ray_u8 = r.RayObject.from_u8(42)
        
        # Create u8 from RayObject
        value_u8 = u8(0, ray_obj=ray_u8)
        
        # Verify values and types
        assert value_u8.value == 42
        assert value_u8.ptr.get_type() == -r.TYPE_U8
        
        # Test with wrong RayObject type
        ray_i64 = r.RayObject.from_i64(42)
        with pytest.raises(ValueError):
            u8(0, ray_obj=ray_i64)
    
    def test_u8_arithmetic(self):
        """Test arithmetic operations for u8."""
        a = u8(50)
        b = u8(30)
        
        # Addition
        result = a + b
        assert isinstance(result, u8)
        assert result.value == 80
        
        # Test addition with overflow
        overflow = u8(200) + u8(100)
        assert overflow.value == 44  # 300 % 256 = 44
        
        # Subtraction
        result = a - b
        assert isinstance(result, u8)
        assert result.value == 20
        
        # Test subtraction with underflow
        underflow = u8(30) - u8(50)
        assert underflow.value == 236  # Wraps around to 256 - 20 = 236
        
        # Multiplication
        result = a * b
        assert isinstance(result, u8)
        assert result.value == 1500 % 256  # 50 * 30 = 1500, but wraps to 1500 % 256 = 220
        
        # Division (integer division)
        result = a // b
        assert isinstance(result, u8)
        assert result.value == 1  # 50 // 30 = 1
        
        # Modulo
        result = a % b
        assert isinstance(result, u8)
        assert result.value == 20  # 50 % 30 = 20
        
        # Division by zero
        with pytest.raises(ZeroDivisionError):
            a // u8(0)
            
        with pytest.raises(ZeroDivisionError):
            a % u8(0)
    
    def test_u8_wrapping(self):
        """Test wrapping behavior for u8 arithmetic."""
        max_u8 = u8(255)
        
        # Addition wrapping
        assert (max_u8 + 1).value == 0
        assert (max_u8 + 2).value == 1
        assert (max_u8 + 255).value == 254
        assert (max_u8 + 256).value == 255
        assert (max_u8 + 257).value == 0
        
        # Subtraction wrapping
        min_u8 = u8(0)
        assert (min_u8 - 1).value == 255
        assert (min_u8 - 2).value == 254
        assert (min_u8 - 255).value == 1
        assert (min_u8 - 256).value == 0
        
        # Multiplication wrapping
        assert (u8(128) * 2).value == 0
        assert (u8(128) * 3).value == 128
        assert (u8(255) * 255).value == 1  # 255 * 255 = 65025, 65025 % 256 = 1
