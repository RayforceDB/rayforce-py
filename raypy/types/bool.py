from typing import Any, Literal

from raypy import _rayforce as r


class _RayBool:
    """
    Base class for Rayforce bool
    """

    ptr: r.RayObject
    ray_type_code: int
    ray_init_method: str
    ray_extr_method: str

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

        if not self.ray_init_method:
            raise AttributeError(
                "Rayforce value init method is not defined for boolean type"
            )

        try:
            self.ptr = getattr(r.RayObject, self.ray_init_method)(value)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    @property
    def value(self) -> bool:
        if not self.ray_extr_method:
            raise AttributeError(
                "Rayforce value extraction is not defined for boolean type"
            )

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
        if isinstance(other, _RayBool):
            return self.value == other.value
        if isinstance(other, bool):
            return self.value == other
        return False


class b8(_RayBool):
    """
    8-bit Rayforce boolean
    """

    ray_type_code = r.TYPE_B8
    ray_init_method = "from_b8"
    ray_extr_method = "get_b8_value"


def from_python_boolean(
    value: bool,
    force_type: Literal["b8"] | None = None,
) -> b8:
    if force_type:
        match force_type:
            case "b8":
                return b8(value)
            case _:
                raise ValueError(f"Unknown type: {force_type}")

    return b8(value)
