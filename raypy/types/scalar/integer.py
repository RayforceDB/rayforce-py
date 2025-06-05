import abc
from typing import Any

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
        value: int | float | str | None = None,
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
            _value = int(value)
        except ValueError as e:
            raise ValueError(f"Expected value of type int, got {type(value)}") from e

        try:
            self.ptr = getattr(r, self.ray_init_method)(_value)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    @property
    def value(self) -> int:
        try:
            return getattr(r, self.ray_extr_method)(self.ptr)
        except Exception as e:
            raise ValueError(f"Error during int type extraction - {str(e)}")

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

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, _RayInteger):
            return self.value < other.value
        return self.value < other

    def __le__(self, other: Any) -> bool:
        if isinstance(other, _RayInteger):
            return self.value <= other.value
        return self.value <= other

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, _RayInteger):
            return self.value > other.value
        return self.value > other

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, _RayInteger):
            return self.value >= other.value
        return self.value >= other


class i16(_RayInteger):
    """
    # Rayforce 16-bit integer
    Analog of Python int (-32768 to 32767)

    ### Init Arguments:
        `value`: float | None - Python int / float / string of an integer
        `ray_obj`: rayforce.RayObject | None - RayObject pointer instance
    """

    # This class represents scalar value, hence code is negative
    ray_type_code = -r.TYPE_I16
    ray_init_method = "init_i16"
    ray_extr_method = "read_i16"


class i32(_RayInteger):
    """
    # Rayforce 32-bit integer
    Analog of Python int (-2147483648 to 2147483647)

    ### Init Arguments:
        `value`: float | None - Python int / float / string of an integer
        `ray_obj`: rayforce.RayObject | None - RayObject pointer instance
    """

    # This class represents scalar value, hence code is negative
    ray_type_code = -r.TYPE_I32
    ray_init_method = "init_i32"
    ray_extr_method = "read_i32"


class i64(_RayInteger):
    """
    # Rayforce 64-bit integer
    Analog of Python int

    ### Init Arguments:
        `value`: float | None - Python int / float / string of an integer
        `ray_obj`: rayforce.RayObject | None - RayObject pointer instance
    """

    # This class represents scalar value, hence code is negative
    ray_type_code = -r.TYPE_I64
    ray_init_method = "init_i64"
    ray_extr_method = "read_i64"
