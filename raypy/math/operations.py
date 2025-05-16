from raypy import _rayforce as r
from raypy.types import container, scalar


ray_add_method = "ray_add"
ray_sub_method = "ray_sub"
ray_mul_method = "ray_mul"
ray_div_method = "ray_div"
ray_fdiv_method = "ray_fdiv"


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


def sub(
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
    Subtract second value from first value of compatible types.

    Supported operations:
    - Scalar - Scalar: i64, f64 with i64, f64
    - Timestamp - Integer: Timestamp with i64
    - Timestamp - Timestamp: Timestamp with Timestamp (returns i64 milliseconds)
    - Vector - Vector: vectors of i64, f64 with vectors of same type and length
    - Vector - Scalar: vectors of i64, f64 with scalar of compatible type
    - Timestamp Vector - Integer: vector of Timestamp with i64

    Args:
        x: First operand (minuend)
        y: Second operand (subtrahend)

    Returns:
        Result of subtraction operation

    Raises:
        ValueError: If operands have incompatible types or dimensions
        TypeError: If there's an error during the subtraction operation
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
            raise ValueError("Can only subtract i64 values from Timestamp vectors")

    elif isinstance(x, scalar.Timestamp):
        if not isinstance(y, (scalar.i64, scalar.Timestamp)):
            raise ValueError("Can only subtract i64 or Timestamp from Timestamp")

    elif isinstance(y, container.Vector) and y.class_type == scalar.Timestamp:
        raise ValueError("Cannot subtract Timestamp vectors")

    elif isinstance(y, scalar.Timestamp):
        if not isinstance(x, scalar.Timestamp):
            raise ValueError("Cannot subtract Timestamp from non-Timestamp value")

    elif isinstance(x, container.Vector):
        if x.class_type not in (scalar.i64, scalar.f64, scalar.Timestamp):
            raise ValueError("Vector must be of type i64, f64 or Timestamp")

        if isinstance(y, container.Vector):
            if not len(x) == len(y):
                raise ValueError("Vectors must be of same length")

            if y.class_type not in (scalar.i64, scalar.f64):
                raise ValueError("Vector must be of type i64 or f64")

        elif not isinstance(y, (scalar.i64, scalar.f64)):
            if x.class_type != scalar.Timestamp or not isinstance(y, scalar.i64):
                raise ValueError("Scalar must be of type i64 or f64")

    elif isinstance(y, container.Vector):
        if y.class_type not in (scalar.i64, scalar.f64):
            raise ValueError("Vector must be of type i64 or f64")

        if not isinstance(x, (scalar.i64, scalar.f64)):
            raise ValueError("Scalar must be of type i64 or f64")

    elif not isinstance(
        x, (scalar.i64, scalar.f64, scalar.Timestamp)
    ) or not isinstance(y, (scalar.i64, scalar.f64, scalar.Timestamp)):
        raise ValueError("Arguments must be of types i64, f64 or Timestamp")

    try:
        ptr = getattr(r.RayObject, ray_sub_method)(x.ptr, y.ptr)
    except Exception as e:
        raise TypeError(f"Error when calling {ray_sub_method} - {str(e)}")

    return container.from_pointer_to_raypy_type(ptr)


def mul(
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
    """
    Multiply two values of compatible types.

    Supported operations:
    - Scalar * Scalar: i64, f64 with i64, f64
    - Vector * Vector: vectors of i64, f64 with vectors of same type and length (element-wise multiplication)
    - Vector * Scalar: vectors of i64, f64 with scalar of compatible type (scalar broadcast)

    Args:
        x: First operand
        y: Second operand

    Returns:
        Result of multiplication operation

    Raises:
        ValueError: If operands have incompatible types or dimensions
        TypeError: If there's an error during the multiplication operation
    """
    if isinstance(x, (scalar.i16, scalar.i32)) or isinstance(
        y, (scalar.i16, scalar.i32)
    ):
        raise ValueError("Types i16 and i32 are not supported. Use i64 instead.")

    if isinstance(x, container.Vector) and x.class_type in (scalar.i16, scalar.i32):
        raise ValueError("Vector types i16 and i32 are not supported. Use i64 instead.")

    if isinstance(y, container.Vector) and y.class_type in (scalar.i16, scalar.i32):
        raise ValueError("Vector types i16 and i32 are not supported. Use i64 instead.")

    if isinstance(x, scalar.Timestamp) or isinstance(y, scalar.Timestamp):
        raise ValueError("Timestamp type is not supported for multiplication")

    if isinstance(x, container.Vector) and x.class_type == scalar.Timestamp:
        raise ValueError("Timestamp vectors are not supported for multiplication")

    if isinstance(y, container.Vector) and y.class_type == scalar.Timestamp:
        raise ValueError("Timestamp vectors are not supported for multiplication")

    if isinstance(x, container.Vector):
        if x.class_type not in (scalar.i64, scalar.f64):
            raise ValueError("Vector must be of type i64 or f64")

        if isinstance(y, container.Vector):
            if not len(x) == len(y):
                raise ValueError("Vectors must be of same length")

            if y.class_type not in (scalar.i64, scalar.f64):
                raise ValueError("Vector must be of type i64 or f64")

        elif not isinstance(y, (scalar.i64, scalar.f64)):
            raise ValueError("Scalar must be of type i64 or f64")

    elif isinstance(y, container.Vector):
        if y.class_type not in (scalar.i64, scalar.f64):
            raise ValueError("Vector must be of type i64 or f64")

        if not isinstance(x, (scalar.i64, scalar.f64)):
            raise ValueError("Scalar must be of type i64 or f64")

    elif not isinstance(x, (scalar.i64, scalar.f64)) or not isinstance(
        y, (scalar.i64, scalar.f64)
    ):
        raise ValueError("Arguments must be of types i64 or f64")

    try:
        ptr = getattr(r.RayObject, ray_mul_method)(x.ptr, y.ptr)
    except Exception as e:
        raise TypeError(f"Error when calling {ray_mul_method} - {str(e)}")

    return container.from_pointer_to_raypy_type(ptr)


def div(
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
    """
    Divide first value by the second value of compatible types.

    This performs integer division for integer types (truncated toward zero).
    For float results, use fdiv().

    Supported operations:
    - Scalar / Scalar: i64, f64 with i64, f64
    - Vector / Vector: vectors of i64, f64 with vectors of same type and length (element-wise division)
    - Vector / Scalar: vectors of i64, f64 with scalar of compatible type (scalar broadcast)

    Args:
        x: Dividend (numerator)
        y: Divisor (denominator)

    Returns:
        Result of division operation

    Raises:
        ValueError: If operands have incompatible types or dimensions, or if divisor is zero
        TypeError: If there's an error during the division operation
    """
    if isinstance(x, (scalar.i16, scalar.i32)) or isinstance(
        y, (scalar.i16, scalar.i32)
    ):
        raise ValueError("Types i16 and i32 are not supported. Use i64 instead.")

    if isinstance(x, container.Vector) and x.class_type in (scalar.i16, scalar.i32):
        raise ValueError("Vector types i16 and i32 are not supported. Use i64 instead.")

    if isinstance(y, container.Vector) and y.class_type in (scalar.i16, scalar.i32):
        raise ValueError("Vector types i16 and i32 are not supported. Use i64 instead.")

    if isinstance(x, scalar.Timestamp) or isinstance(y, scalar.Timestamp):
        raise ValueError("Timestamp type is not supported for division")

    if isinstance(x, container.Vector) and x.class_type == scalar.Timestamp:
        raise ValueError("Timestamp vectors are not supported for division")

    if isinstance(y, container.Vector) and y.class_type == scalar.Timestamp:
        raise ValueError("Timestamp vectors are not supported for division")

    # Check for scalar zero division
    if not isinstance(y, container.Vector) and isinstance(y, (scalar.i64, scalar.f64)):
        if y.value == 0:
            raise ValueError("Division by zero")

    if isinstance(x, container.Vector):
        if x.class_type not in (scalar.i64, scalar.f64):
            raise ValueError("Vector must be of type i64 or f64")

        if isinstance(y, container.Vector):
            if not len(x) == len(y):
                raise ValueError("Vectors must be of same length")

            if y.class_type not in (scalar.i64, scalar.f64):
                raise ValueError("Vector must be of type i64 or f64")

            # Check for vector zero division
            for item in y.to_list():
                if item.value == 0:
                    raise ValueError("Division by zero in vector")

        elif not isinstance(y, (scalar.i64, scalar.f64)):
            raise ValueError("Scalar must be of type i64 or f64")

    elif isinstance(y, container.Vector):
        if y.class_type not in (scalar.i64, scalar.f64):
            raise ValueError("Vector must be of type i64 or f64")

        if not isinstance(x, (scalar.i64, scalar.f64)):
            raise ValueError("Scalar must be of type i64 or f64")

        # Check for vector zero division
        for item in y.to_list():
            if item.value == 0:
                raise ValueError("Division by zero in vector")

    elif not isinstance(x, (scalar.i64, scalar.f64)) or not isinstance(
        y, (scalar.i64, scalar.f64)
    ):
        raise ValueError("Arguments must be of types i64 or f64")

    try:
        ptr = getattr(r.RayObject, ray_div_method)(x.ptr, y.ptr)
    except Exception as e:
        raise TypeError(f"Error when calling {ray_div_method} - {str(e)}")

    return container.from_pointer_to_raypy_type(ptr)


def fdiv(
    x: scalar.i64
    | scalar.f64
    | container.Vector[scalar.i64]
    | container.Vector[scalar.f64],
    y: scalar.i64
    | scalar.f64
    | container.Vector[scalar.i64]
    | container.Vector[scalar.f64],
) -> scalar.f64 | container.Vector[scalar.f64]:
    """
    Perform floating-point division of first value by the second value.

    Unlike div(), this always returns floating-point results.

    Supported operations:
    - Scalar / Scalar: i64, f64 with i64, f64
    - Vector / Vector: vectors of i64, f64 with vectors of same type and length (element-wise division)
    - Vector / Scalar: vectors of i64, f64 with scalar of compatible type (scalar broadcast)
    - Scalar / Vector: scalar divided by vector elements (element-wise)

    Args:
        x: Dividend (numerator)
        y: Divisor (denominator)

    Returns:
        Result of floating-point division operation as scalar.f64 or Vector[f64]

    Raises:
        ValueError: If operands have incompatible types or dimensions, or if divisor is zero
        TypeError: If there's an error during the division operation
    """
    if isinstance(x, (scalar.i16, scalar.i32)) or isinstance(
        y, (scalar.i16, scalar.i32)
    ):
        raise ValueError("Types i16 and i32 are not supported. Use i64 instead.")

    if isinstance(x, container.Vector) and x.class_type in (scalar.i16, scalar.i32):
        raise ValueError("Vector types i16 and i32 are not supported. Use i64 instead.")

    if isinstance(y, container.Vector) and y.class_type in (scalar.i16, scalar.i32):
        raise ValueError("Vector types i16 and i32 are not supported. Use i64 instead.")

    if isinstance(x, scalar.Timestamp) or isinstance(y, scalar.Timestamp):
        raise ValueError("Timestamp type is not supported for division")

    if isinstance(x, container.Vector) and x.class_type == scalar.Timestamp:
        raise ValueError("Timestamp vectors are not supported for division")

    if isinstance(y, container.Vector) and y.class_type == scalar.Timestamp:
        raise ValueError("Timestamp vectors are not supported for division")

    # Check for scalar zero division
    if not isinstance(y, container.Vector) and isinstance(y, (scalar.i64, scalar.f64)):
        if y.value == 0:
            raise ValueError("Division by zero")

    if isinstance(x, container.Vector):
        if x.class_type not in (scalar.i64, scalar.f64):
            raise ValueError("Vector must be of type i64 or f64")

        if isinstance(y, container.Vector):
            if not len(x) == len(y):
                raise ValueError("Vectors must be of same length")

            if y.class_type not in (scalar.i64, scalar.f64):
                raise ValueError("Vector must be of type i64 or f64")

            # Check for vector zero division
            for item in y.to_list():
                if item.value == 0:
                    raise ValueError("Division by zero in vector")

        elif not isinstance(y, (scalar.i64, scalar.f64)):
            raise ValueError("Scalar must be of type i64 or f64")

    elif isinstance(y, container.Vector):
        if y.class_type not in (scalar.i64, scalar.f64):
            raise ValueError("Vector must be of type i64 or f64")

        if not isinstance(x, (scalar.i64, scalar.f64)):
            raise ValueError("Scalar must be of type i64 or f64")

        # Check for vector zero division
        for item in y.to_list():
            if item.value == 0:
                raise ValueError("Division by zero in vector")

    elif not isinstance(x, (scalar.i64, scalar.f64)) or not isinstance(
        y, (scalar.i64, scalar.f64)
    ):
        raise ValueError("Arguments must be of types i64 or f64")

    try:
        ptr = getattr(r.RayObject, ray_fdiv_method)(x.ptr, y.ptr)
    except Exception as e:
        raise TypeError(f"Error when calling {ray_fdiv_method} - {str(e)}")

    return container.from_pointer_to_raypy_type(ptr)
