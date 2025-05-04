import abc
from typing import Any, Literal

from raypy import _rayforce as r


class _RayInteger(abc.ABC):
    """
    Base class for Rayforce integers (i16, i32, i64)
    """

    ptr: r.RayObject

    ray_type_code: int
    ray_init_method: str
    ray_extr_method: str

    def __init__(
        self,
        value: int | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if value is None and ray_obj is None:
            raise ValueError("At least one argument is required")

        if ray_obj is not None:
            if (_type := ray_obj.get_type()) != -self.ray_type_code:
                raise ValueError(
                    f"Expected RayForce object of type {self.ray_type_code}, got {_type}"
                )
            self.ptr = ray_obj
            return

        try:
            value = int(value)
        except ValueError as e:
            raise ValueError(f"Expected value of type int, got {type(value)}") from e

        if not self.ray_init_method:
            raise AttributeError(
                "Rayforce value init method is not defined for integer type"
            )

        try:
            self.ptr = getattr(r.RayObject, self.ray_init_method)(value)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    @property
    def value(self) -> int:
        if not self.ray_extr_method:
            raise AttributeError(
                "Rayforce value extraction is not defined for integer type"
            )

        try:
            return getattr(self.ptr, self.ray_extr_method)()
        except TypeError as e:
            raise TypeError(
                f"Expected RayObject type of {self.ray_type_code}, got {self.ptr.get_type()}"
            ) from e

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, _RayInteger):
            return self.value == other.value
        return self.value == other


class i16(_RayInteger):
    """
    16-bit Rayforce integer
    """

    ray_type_code = r.TYPE_I16
    ray_init_method = "from_i16"
    ray_extr_method = "get_i16_value"


class i32(_RayInteger):
    """
    16-bit Rayforce integer
    """

    ray_type_code = r.TYPE_I32
    ray_init_method = "from_i32"
    ray_extr_method = "get_i32_value"


class i64(_RayInteger):
    """
    64-bit Rayforce integer
    """

    ray_type_code = r.TYPE_I64
    ray_init_method = "from_i64"
    ray_extr_method = "get_i64_value"
