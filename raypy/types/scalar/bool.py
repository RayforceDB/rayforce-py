from typing import Any

from raypy import _rayforce as r


class b8:
    """
    # Rayforce boolean
    Analog of Python boolean

    ### Init Arguments:
        `value`: Any | None - Instance, which could be converted to bool using bool(value).
        `ray_obj`: rayforce.RayObject | None - RayObject pointer instance.
    """

    ptr: r.RayObject

    # This class represents scalar value, hence code is negative
    ray_type_code = -r.TYPE_B8

    ray_init_method = "init_b8"
    ray_extr_method = "read_b8"

    def __init__(
        self,
        value: Any | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if value is None and ray_obj is None:
            raise ValueError("At least one initialisatiion is required")

        if ray_obj is not None:
            if (_type := ray_obj.get_obj_type()) != self.ray_type_code:
                raise ValueError(
                    f"Expected RayObject of type {self.ray_type_code}, got {_type}"
                )

            self.ptr = ray_obj
            return

        try:
            _value = bool(value)
        except ValueError as e:
            raise ValueError(f"Expected value of type bool, got {type(_value)}") from e

        try:
            self.ptr = getattr(r, self.ray_init_method)(value)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during b8 type initialisation - {str(e)}")

    @property
    def value(self) -> bool:
        try:
            return getattr(r, self.ray_extr_method)(self.ptr)
        except Exception as e:
            raise ValueError(f"Error during b8 type extraction - {str(e)}")

    def __bool__(self) -> bool:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"b8({self.value})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, b8):
            return self.value == other.value
        if isinstance(other, bool):
            return self.value == other
        return False
