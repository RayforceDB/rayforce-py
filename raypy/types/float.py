from typing import Any, Literal

from raypy import _rayforce as r


class _RayFloat:
    """
    Base class for Rayforce float
    """

    ptr: r.RayObject
    ray_type_code: int
    ray_init_method: str
    ray_extr_method: str

    def __init__(self, value: float, ray_obj: r.RayObject | None = None) -> None:
        if ray_obj is not None:
            if (_type := ray_obj.get_type()) != -self.ray_type_code:
                raise ValueError(
                    f"Expected RayForce object of type {self.ray_type_code}, got {_type}"
                )
            self.ptr = ray_obj
            return

        try:
            value = float(value)
        except ValueError as e:
            raise ValueError(f"Expected value of type float, got {type(value)}") from e

        if not self.ray_init_method:
            raise AttributeError(
                "Rayforce value init method is not defined for float type"
            )

        try:
            self.ptr = getattr(r.RayObject, self.ray_init_method)(value)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    @property
    def value(self) -> float:
        if not self.ray_extr_method:
            raise AttributeError(
                "Rayforce value extraction is not defined for float type"
            )

        try:
            return getattr(self.ptr, self.ray_extr_method)()
        except TypeError as e:
            raise TypeError(
                f"Expected RayObject type of {self.ray_type_code}, got {self.ptr.get_type()}"
            ) from e

    def __float__(self) -> float:
        return float(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    def __eq__(self, other: Any):
        if isinstance(other, _RayFloat):
            return self.value == other.value
        return self.value == other


class f64(_RayFloat):
    """
    64-bit Rayforce float
    """

    ray_type_code = r.TYPE_F64
    ray_init_method = "from_f64"
    ray_extr_method = "get_f64_value"


def from_python_float(
    value: float,
    force_type: Literal["f64"] | None = None,
) -> f64:
    if force_type:
        match force_type:
            case "f64":
                return f64(value)
            case _:
                raise ValueError(f"Unknown type: {force_type}")

    return f64(value)
