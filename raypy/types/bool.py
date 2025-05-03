from typing import Any

from raypy import _rayforce as r


class b8:
    """
    8-bit Rayforce boolean
    """

    ptr: r.RayObject

    ray_type_code = r.TYPE_B8
    ray_init_method = "from_b8"
    ray_extr_method = "get_b8_value"

    def __init__(self, value: bool, ray_obj: r.RayObject | None = None) -> None:
        if ray_obj is not None:
            if (_type := ray_obj.get_type()) != -self.ray_type_code:
                raise ValueError(
                    f"Expected RayForce object of type {self.ray_type_code}, got {_type}"
                )
            self.ptr = ray_obj
            return

        try:
            value = bool(value)
        except ValueError as e:
            raise ValueError(f"Expected value of type bool, got {type(value)}") from e

        try:
            self.ptr = getattr(r.RayObject, self.ray_init_method)(value)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    @property
    def value(self) -> bool:
        try:
            return getattr(self.ptr, self.ray_extr_method)()
        except TypeError as e:
            raise TypeError(
                f"Expected RayObject type of {self.ray_type_code}, got {self.ptr.get_type()}"
            ) from e

    def __bool__(self) -> bool:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"B8({self.value})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, b8):
            return self.value == other.value
        if isinstance(other, bool):
            return self.value == other
        return False
