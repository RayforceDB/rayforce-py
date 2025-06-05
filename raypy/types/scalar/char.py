from typing import Any

from raypy import _rayforce as r


class c8:
    """
    # Rayforce Char type
    Has no Python equivalent

    ### Init Arguments:
        `value`: str | int | None - Char value, or integer representation of unicode char.
        `ray_obj`: rayforce.RayObject | None - RayObject pointer instance.
    """

    ptr: r.RayObject

    # This class represents scalar value, hence code is negative
    ray_type_code = -r.TYPE_C8

    ray_init_method = "init_c8"
    ray_extr_method = "read_c8"

    def __init__(
        self,
        value: str | int | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if value is None and ray_obj is None:
            raise ValueError("At least one initialisation argument is required")

        if ray_obj is not None:
            if (_type := ray_obj.get_obj_type()) != self.ray_type_code:
                raise ValueError(
                    f"Expected RayObject of type {self.ray_type_code}, got {_type}"
                )

            self.ptr = ray_obj
            return

        if isinstance(value, str):
            if len(value) == 1:
                # If unicode value of given char is not supported, set it as "A"
                char_value = "A" if ord(value) > 127 else value
            else:
                raise ValueError(
                    "Character must be a single character string or an integer (0-126)"
                )
        elif isinstance(value, int):
            if 0 <= value <= 126:
                char_value = chr(value)
            else:
                raise ValueError(
                    "Integer representation of a char should be between 0 and 126"
                )
        else:
            raise ValueError(
                "Character must be a single character string or an integer (0-126)"
            )

        try:
            self.ptr = getattr(r, self.ray_init_method)(char_value)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during c8 type initialisation - {str(e)}")

    @property
    def value(self) -> str:
        try:
            return getattr(r, self.ray_extr_method)(self.ptr)
        except Exception as e:
            raise ValueError(f"Error during b8 type extraction - {str(e)}")

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
