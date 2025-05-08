from raypy import _rayforce as r
from raypy.types import container, scalar


ray_add_method = "ray_add"


def add(
    x: scalar.i64
    | scalar.f64
    | container.Vector[scalar.i64]
    | container.Vector[scalar.f64],
    y: scalar.i64
    | scalar.f64
    | container.Vector[scalar.i64]
    | container.Vector[scalar.f64],
) -> (
    scalar.i64
    | scalar.f64
    | container.Vector[scalar.i64]
    | container.Vector[scalar.f64]
):
    for arg in (x, y):
        if isinstance(arg, container.Vector):
            if arg.class_type not in (scalar.i64, scalar.f64):
                raise ValueError("Vector has to be of type i64 or f64")
        elif not isinstance(arg, (scalar.i64, scalar.f64)):
            raise ValueError(
                "Argument has to be of type i64 or f64 or Vector of these types"
            )

    try:
        ptr = getattr(r.RayObject, ray_add_method)(x.ptr, y.ptr)
    except Exception as e:
        raise TypeError(f"Error when calling {ray_add_method} - {str(e)}")

    return container.from_pointer_to_raypy_type(ptr)
