from typing import Any

from raypy import _rayforce as r


class c8:
    """
    Rayforce char type
    """

    ptr: r.RayObject

    ray_type_code = r.TYPE_C8
    ray_init_method = "from_c8"
    ray_extr_method = "get_c8_value"

    def __init__(
        self,
        value: str | int,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if ray_obj is not None:
            if (_type := ray_obj.get_type()) != -self.ray_type_code:
                raise ValueError(
                    f"Expected RayForce object of type {self.ray_type_code}, got {_type}"
                )
            self.ptr = ray_obj
            return

        if isinstance(value, str) and len(value) == 1:
            if ord(value) > 127:
                char_value = "A"
            else:
                char_value = value
        elif isinstance(value, int) and 0 <= value <= 126:
            char_value = chr(value)
        else:
            raise ValueError(
                "Character must be a single character string or an integer (0-126)"
            )

        try:
            self.ptr = getattr(r.RayObject, self.ray_init_method)(char_value)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    @property
    def value(self) -> str:
        try:
            return getattr(self.ptr, self.ray_extr_method)()
        except TypeError as e:
            raise TypeError(
                f"Expected RayObject type of {self.ray_type_code}, got {self.ptr.get_type()}"
            ) from e

    @property
    def code(self) -> int:
        return ord(self.value)

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"c8({self.value})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, c8):
            return self.value == other.value
        if isinstance(other, str) and len(other) == 1:
            return self.value == other
        return False
