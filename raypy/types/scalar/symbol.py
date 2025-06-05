from typing import Any

from raypy import _rayforce as r


class Symbol:
    """
    # Rayforce Symbol type
    Analog of Python string

    ### Init Arguments:
        `value`: float | None - Python stringable type
        `ray_obj`: rayforce.RayObject | None - RayObject pointer instance
    """

    ptr: r.RayObject

    # This class represents scalar value, hence code is negative
    ray_type_code = -r.TYPE_SYMBOL

    ray_init_method = "init_symbol"
    ray_extr_method = "read_symbol"

    def __init__(
        self,
        value: str | Any | None = None,
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

        _value = str(value)

        try:
            self.ptr = getattr(r, self.ray_init_method)(_value)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    @property
    def value(self) -> str:
        try:
            return getattr(r, self.ray_extr_method)(self.ptr)
        except Exception as e:
            raise TypeError(f"Error during symbol type extraction - {str(e)}") from e

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

    def __hash__(self):
        return hash(self.value)

    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)
