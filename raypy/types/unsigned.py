from __future__ import annotations

from typing import Any

from raypy import _rayforce as r


class u8:
    """
    8-bit Rayforce unsigned type
    """

    ptr: r.RayObject

    ray_type_code = r.TYPE_U8
    ray_init_method = "from_u8"
    ray_extr_method = "get_u8_value"

    def __init__(self, value: bool, ray_obj: r.RayObject | None = None) -> None:
        if ray_obj is not None:
            if (_type := ray_obj.get_type()) != -self.ray_type_code:
                raise ValueError(
                    f"Expected RayForce object of type {self.ray_type_code}, got {_type}"
                )
            self.ptr = ray_obj
            return

        if not isinstance(value, int):
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise ValueError(f"Expected value of type bool, got {type(value)}")

        if value < 0 or value > 255:
            raise ValueError("Unsigned value must be in range 0-255")

        try:
            self.ptr = getattr(r.RayObject, self.ray_init_method)(value)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    @property
    def value(self) -> int:
        try:
            return getattr(self.ptr, self.ray_extr_method)()
        except TypeError as e:
            raise TypeError(
                f"Expected RayObject type of {self.ray_type_code}, got {self.ptr.get_type()}"
            ) from e

    def __int__(self) -> int:
        return self.value

    def __index__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"u8({self.value})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, u8):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        return False

    def __add__(self, other: Any) -> u8:
        if isinstance(other, u8):
            other = other.value
        result = self.value + other
        # Wrap around on overflow
        result = result & 0xFF
        return u8(result)

    def __sub__(self, other: Any) -> u8:
        if isinstance(other, u8):
            other = other.value
        result = self.value - other
        # Wrap around on underflow
        result = result & 0xFF
        return u8(result)

    def __mul__(self, other: Any) -> u8:
        if isinstance(other, u8):
            other = other.value
        result = self.value * other
        # Wrap around on overflow
        result = result & 0xFF
        return u8(result)
    
    def __floordiv__(self, other: Any) -> u8:
        if isinstance(other, u8):
            other = other.value
        if other == 0:
            raise ZeroDivisionError("division by zero")
        result = self.value // other
        return u8(result)

    def __mod__(self, other: Any) -> u8:
        if isinstance(other, u8):
            other = other.value
        if other == 0:
            raise ZeroDivisionError("modulo by zero")
        result = self.value % other
        return u8(result)
