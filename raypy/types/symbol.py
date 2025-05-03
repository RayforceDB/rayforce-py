from typing import Any

from raypy import _rayforce as r


class Symbol:
    """
    Rayforce Symbol type
    """

    ptr: r.RayObject

    ray_type_code = r.TYPE_SYMBOL
    ray_init_method = "from_symbol"
    ray_extr_method = "get_symbol_value"

    def __init__(
        self,
        value: str,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if ray_obj is not None:
            if (_type := ray_obj.get_type()) != -self.ray_type_code:
                raise ValueError(
                    f"Expected RayForce object of type {self.ray_type_code}, got {_type}"
                )
            self.ptr = ray_obj
            return

        if not isinstance(value, str):
            value = str(value)

        try:
            self.ptr = getattr(r.RayObject, self.ray_init_method)(value)
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

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Symbol({self.value})"

    def __eq__(self, other: Any) -> bool:
        """Equality comparison."""
        if isinstance(other, Symbol):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return False
