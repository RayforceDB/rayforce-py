from typing import Any

from raypy import _rayforce as r


class RaypyScalar:
    ptr: r.RayObject
    _type: int

    def __init__(
        self,
        value: Any | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if value is None and ray_obj is None:
            raise ValueError("At least one initialization argument is required")

        if self._type is None:
            raise AttributeError("Scalar type code is not set")

        if ray_obj is not None:
            if (
                not isinstance(ray_obj, r.RayObject)
                or (_type := ray_obj.get_obj_type()) != self._type
            ):
                raise ValueError(
                    f"Expected RayObject of type {self._type}, got {_type}"
                )

            self.ptr = ray_obj


class RaypyContainer(RaypyScalar): ...
