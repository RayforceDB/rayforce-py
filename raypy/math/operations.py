from raypy import _rayforce as r
from raypy.types import container, scalar


ray_add_method = "ray_add"


def add(
    x: scalar.i64
    | scalar.f64
    | container.Vector[scalar.i64]
    | container.Vector[scalar.f64]
    | scalar.Timestamp,
    y: scalar.i64
    | scalar.f64
    | container.Vector[scalar.i64]
    | container.Vector[scalar.f64]
    | scalar.Timestamp,
) -> (
    scalar.i64
    | scalar.f64
    | container.Vector[scalar.i64]
    | container.Vector[scalar.f64]
    | scalar.Timestamp
):
    if isinstance(x, container.Vector):
        if x.class_type == scalar.Timestamp:
            if not isinstance(y, scalar.i64):
                raise ValueError("Provide an US i64 value to add to timestamp vector")

        if x.class_type not in (scalar.i64, scalar.f64):
            raise ValueError("Vector has to be of type i64 or f64")
    elif not isinstance(x, (scalar.i64, scalar.f64, scalar.Timestamp)):
        raise ValueError(
            "Argument has to be of type i64 or f64 or Timestamp or Vector of these types"
        )

    if isinstance(y, container.Vector):
        if y.class_type == scalar.Timestamp:
            if not isinstance(x, scalar.i64):
                raise ValueError("Provide an US i64 value to add to timestamp vector")

        if y.class_type not in (scalar.i64, scalar.f64):
            raise ValueError("Vector has to be of type i64 or f64")
    elif not isinstance(y, (scalar.i64, scalar.f64, scalar.Timestamp)):
        raise ValueError(
            "Argument has to be of type i64 or f64 or Timestamp or Vector of these types"
        )

    try:
        ptr = getattr(r.RayObject, ray_add_method)(x.ptr, y.ptr)
    except Exception as e:
        raise TypeError(f"Error when calling {ray_add_method} - {str(e)}")

    return container.from_pointer_to_raypy_type(ptr)
