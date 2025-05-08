from raypy import _rayforce as r
from raypy.types import container, scalar


ray_add_method = "ray_add"


def add(
    x: scalar.i64
    | scalar.f64
    | scalar.Timestamp
    | container.Vector[scalar.i64]
    | container.Vector[scalar.f64]
    | container.Vector[scalar.Timestamp],
    y: scalar.i64
    | scalar.f64
    | scalar.Timestamp
    | container.Vector[scalar.i64]
    | container.Vector[scalar.f64]
    | container.Vector[scalar.Timestamp],
) -> (
    scalar.i64
    | scalar.f64
    | scalar.Timestamp
    | container.Vector[scalar.i64]
    | container.Vector[scalar.f64]
    | container.Vector[scalar.Timestamp]
):
    """
    Add two values of compatible types.

    Supported operations:
    - Scalar + Scalar: i64, f64 with i64, f64
    - Timestamp + Integer: Timestamp with i64
    - Vector + Vector: vectors of i64, f64 with vectors of same type and length
    - Vector + Scalar: vectors of i64, f64 with scalar of compatible type
    - Timestamp Vector + Integer: vector of Timestamp with i64

    Args:
        x: First operand
        y: Second operand

    Returns:
        Result of addition operation

    Raises:
        ValueError: If operands have incompatible types or dimensions
        TypeError: If there's an error during the addition operation
    """
    if isinstance(x, (scalar.i16, scalar.i32)) or isinstance(
        y, (scalar.i16, scalar.i32)
    ):
        raise ValueError("Types i16 and i32 are not supported. Use i64 instead.")

    if isinstance(x, container.Vector) and x.class_type in (scalar.i16, scalar.i32):
        raise ValueError("Vector types i16 and i32 are not supported. Use i64 instead.")

    if isinstance(y, container.Vector) and y.class_type in (scalar.i16, scalar.i32):
        raise ValueError("Vector types i16 and i32 are not supported. Use i64 instead.")

    if isinstance(x, container.Vector) and x.class_type == scalar.Timestamp:
        if not isinstance(y, scalar.i64):
            raise ValueError("Can only add i64 values to Timestamp vectors")

    elif isinstance(x, scalar.Timestamp):
        if not isinstance(y, scalar.i64):
            raise ValueError("Can only add i64 values to Timestamp")

    elif isinstance(y, container.Vector) and y.class_type == scalar.Timestamp:
        if not isinstance(x, scalar.i64):
            raise ValueError("Can only add i64 values to Timestamp vectors")

    elif isinstance(y, scalar.Timestamp):
        if not isinstance(x, scalar.i64):
            raise ValueError("Can only add i64 values to Timestamp")

    elif isinstance(x, container.Vector):
        if x.class_type not in (scalar.i64, scalar.f64, scalar.Timestamp):
            raise ValueError("Vector must be of type i64, f64 or Timestamp")

        if isinstance(y, container.Vector):
            if not len(x) == len(y):
                raise ValueError("Vectors must be of same length")

            if y.class_type not in (scalar.i64, scalar.f64, scalar.Timestamp):
                raise ValueError("Vector must be of type i64, f64 or Timestamp")

        elif not isinstance(y, (scalar.i64, scalar.f64)):
            if x.class_type != scalar.Timestamp or not isinstance(y, scalar.i64):
                raise ValueError("Scalar must be of type i64 or f64")

    elif isinstance(y, container.Vector):
        if y.class_type not in (scalar.i64, scalar.f64, scalar.Timestamp):
            raise ValueError("Vector must be of type i64, f64 or Timestamp")

        if not isinstance(x, (scalar.i64, scalar.f64)):
            if y.class_type != scalar.Timestamp or not isinstance(x, scalar.i64):
                raise ValueError("Scalar must be of type i64 or f64")

    elif not isinstance(
        x, (scalar.i64, scalar.f64, scalar.Timestamp)
    ) or not isinstance(y, (scalar.i64, scalar.f64, scalar.Timestamp)):
        raise ValueError("Arguments must be of types i64, f64 or Timestamp")

    try:
        ptr = getattr(r.RayObject, ray_add_method)(x.ptr, y.ptr)
    except Exception as e:
        raise TypeError(f"Error when calling {ray_add_method} - {str(e)}")

    return container.from_pointer_to_raypy_type(ptr)
