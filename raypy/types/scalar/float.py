from typing import Any

from raypy import _rayforce as r


class f64:
    """
    # Rayforce float
    Analog of Python float

    ### Init Arguments:
        `value`: float | None - Python int or float type
        `ray_obj`: rayforce.RayObject | None - RayObject pointer instance
    """

    ptr: r.RayObject

    # This class represents scalar value, hence code is negative
    ray_type_code = -r.TYPE_F64

    ray_init_method = "init_f64"
    ray_extr_method = "from_f64"

    def __init__(
        self,
        value: int | float | None = None,
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

        try:
            _value = float(value)
        except ValueError as e:
            raise ValueError(f"Expected value of type float, got {type(value)}") from e

        try:
            self.ptr = getattr(r, self.ray_init_method)(_value)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    @property
    def value(self) -> float:
        try:
            return getattr(r, self.ray_extr_method)(self.ptr)
        except Exception as e:
            raise ValueError(f"Error during f8 type extraction - {str(e)}")

    def __float__(self) -> float:
        return float(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"f64({self.value})"

    def __eq__(self, other: Any):
        if isinstance(other, f64):
            return self.value == other.value
        return self.value == other
