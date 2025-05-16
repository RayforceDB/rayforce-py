from raypy import _rayforce as r
from raypy.types import container, scalar


ray_add_method = "ray_add"
ray_sub_method = "ray_sub"
ray_mul_method = "ray_mul"
ray_div_method = "ray_div"
ray_fdiv_method = "ray_fdiv"
ray_mod_method = "ray_mod"
ray_sum_method = "ray_sum"
ray_avg_method = "ray_avg"
ray_med_method = "ray_med"
ray_dev_method = "ray_dev"
ray_min_method = "ray_min"
ray_max_method = "ray_max"


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

            if y.class_type not in (scalar.i64, scalar.f64):
                raise ValueError("Vector must be of type i64 or f64")

        elif not isinstance(y, (scalar.i64, scalar.f64)):
            if x.class_type != scalar.Timestamp or not isinstance(y, scalar.i64):
                raise ValueError("Scalar must be of type i64 or f64")

    elif isinstance(y, container.Vector):
        if y.class_type not in (scalar.i64, scalar.f64):
            raise ValueError("Vector must be of type i64 or f64")

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


def mod(
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
    Perform modulo operation of first value by the second value.

    Supported operations:
    - Scalar % Scalar: i64, f64 with i64, f64
    - Vector % Vector: vectors of i64, f64 with vectors of same type and length (element-wise modulo)
    - Vector % Scalar: vectors of i64, f64 with scalar of compatible type (scalar broadcast)

    Args:
        x: First operand (dividend)
        y: Second operand (divisor)

    Returns:
        Result of modulo operation

    Raises:
        ValueError: If operands have incompatible types or dimensions, or if divisor is zero
        TypeError: If there's an error during the modulo operation
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
        raise ValueError("Timestamp type is not supported for modulo")

    if isinstance(x, container.Vector) and x.class_type == scalar.Timestamp:
        raise ValueError("Timestamp vectors are not supported for modulo")

    if isinstance(y, container.Vector) and y.class_type == scalar.Timestamp:
        raise ValueError("Timestamp vectors are not supported for modulo")

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
        ptr = getattr(r.RayObject, ray_mod_method)(x.ptr, y.ptr)
    except Exception as e:
        raise TypeError(f"Error when calling {ray_mod_method} - {str(e)}")

    return container.from_pointer_to_raypy_type(ptr)


def sum(
    x: scalar.i64
    | scalar.f64
    | container.Vector[scalar.i64]
    | container.Vector[scalar.f64],
) -> scalar.i64 | scalar.f64:
    """
    Calculate the sum of a scalar or all elements in a vector.

    For scalar inputs, the function returns the input value.
    For vector inputs, it returns the sum of all elements.

    Args:
        x: Scalar or vector of i64 or f64 values

    Returns:
        Scalar value (input value for scalars, sum of elements for vectors)

    Raises:
        ValueError: If input is not a supported type
        TypeError: If there's an error during the sum operation
    """
    # Handle scalar inputs directly
    if isinstance(x, (scalar.i64, scalar.f64)):
        return x

    # Handle vector inputs
    if isinstance(x, container.Vector):
        if x.class_type not in (scalar.i64, scalar.f64):
            raise ValueError("Vector must be of type i64 or f64")

        try:
            ptr = getattr(r.RayObject, ray_sum_method)(x.ptr)
        except Exception as e:
            raise TypeError(f"Error when calling {ray_sum_method} - {str(e)}")

        return container.from_pointer_to_raypy_type(ptr)

    raise ValueError("Input must be a scalar or vector of type i64 or f64")


def avg(
    x: scalar.i64 | scalar.f64 | container.Vector[scalar.i64],
) -> scalar.f64:
    """
    Calculate the average of a scalar or all elements in a vector.

    For scalar inputs, the function returns the input value as a float.
    For vector inputs, it returns the mean of all elements.
    For empty vectors, returns 0.0.
    For vectors with a single element, returns that element as a float.

    Note: F64 vectors are not supported by the core implementation.

    Args:
        x: Scalar (i64, f64) or vector of i64 values

    Returns:
        Scalar f64 value representing the average

    Raises:
        ValueError: If input is not a supported type
        TypeError: If there's an error during the calculation
    """
    if not isinstance(x, (scalar.i64, scalar.f64, container.Vector)):
        raise ValueError("Input must be a scalar or vector of type i64 or f64")

    if isinstance(x, container.Vector):
        if x.class_type == scalar.f64:
            raise ValueError("F64 vectors are not supported for average operation")
        if x.class_type not in (scalar.i64,):
            raise ValueError("Vector must be of type i64")

    try:
        ptr = getattr(r.RayObject, ray_avg_method)(x.ptr)
    except Exception as e:
        raise TypeError(f"Error when calling {ray_avg_method} - {str(e)}")

    return container.from_pointer_to_raypy_type(ptr)


def med(
    x: scalar.i64 | scalar.f64 | container.Vector[scalar.i64],
) -> scalar.f64:
    """
    Calculate the median of a scalar or all elements in a vector.

    The median is the middle value of a dataset. It is the value that separates
    the higher half from the lower half of the data.

    For scalar inputs, the function returns the input value as a float.
    For vector inputs with odd length, returns the middle value.
    For vector inputs with even length, returns the average of the two middle values.
    For empty vectors, returns 0.0.
    For vectors with a single element, returns that element as a float.

    Note: F64 vectors are not supported by the core implementation.

    Args:
        x: Scalar (i64, f64) or vector of i64 values

    Returns:
        Scalar f64 value representing the median

    Raises:
        ValueError: If input is not a supported type
        TypeError: If there's an error during the calculation
    """
    if not isinstance(x, (scalar.i64, scalar.f64, container.Vector)):
        raise ValueError("Input must be a scalar or vector of type i64 or f64")

    if isinstance(x, container.Vector):
        if x.class_type == scalar.f64:
            raise ValueError("F64 vectors are not supported for median operation")
        if x.class_type not in (scalar.i64,):
            raise ValueError("Vector must be of type i64")

    try:
        ptr = getattr(r.RayObject, ray_med_method)(x.ptr)
    except Exception as e:
        raise TypeError(f"Error when calling {ray_med_method} - {str(e)}")

    return container.from_pointer_to_raypy_type(ptr)


def dev(
    x: scalar.i64 | scalar.f64 | container.Vector[scalar.i64],
) -> scalar.f64:
    """
    Calculate the standard deviation of a scalar or vector.

    For a scalar, this will always return 0.0.
    For a vector, this will calculate the standard deviation of all values.

    Args:
        x: Value to calculate standard deviation of

    Returns:
        Standard deviation as a f64 scalar

    Raises:
        ValueError: If the input vector is not of type i64
        TypeError: If there's an error during the standard deviation calculation
    """
    if isinstance(x, container.Vector):
        if x.class_type == scalar.f64:
            raise ValueError(
                "F64 vectors are not supported for standard deviation operation"
            )
        elif x.class_type != scalar.i64:
            raise ValueError("Vector must be of type i64")

    elif not isinstance(x, (scalar.i64, scalar.f64)):
        raise ValueError(
            "Input must be a scalar of type i64 or f64, or a vector of type i64"
        )

    try:
        ptr = getattr(r.RayObject, ray_dev_method)(x.ptr)
    except Exception as e:
        raise TypeError(f"Error when calling {ray_dev_method} - {str(e)}")

    return container.from_pointer_to_raypy_type(ptr)


def min(
    x: scalar.i64 | scalar.f64 | container.Vector[scalar.i64],
) -> scalar.i64 | scalar.f64:
    """
    Find the minimum value in a scalar or vector.

    For a scalar, this will return the scalar itself.
    For a vector, this will find the minimum value of all elements.

    Args:
        x: Value to find minimum of

    Returns:
        Minimum value as a scalar (same type as input for scalars, i64 for i64 vectors)

    Raises:
        ValueError: If the input vector is not of type i64
        TypeError: If there's an error during the minimum calculation
    """
    if isinstance(x, container.Vector):
        if x.class_type == scalar.f64:
            raise ValueError("F64 vectors are not supported for minimum operation")
        elif x.class_type != scalar.i64:
            raise ValueError("Vector must be of type i64")

    elif not isinstance(x, (scalar.i64, scalar.f64)):
        raise ValueError(
            "Input must be a scalar of type i64 or f64, or a vector of type i64"
        )

    try:
        ptr = getattr(r.RayObject, ray_min_method)(x.ptr)
    except Exception as e:
        raise TypeError(f"Error when calling {ray_min_method} - {str(e)}")

    return container.from_pointer_to_raypy_type(ptr)


def max(
    x: scalar.i64 | scalar.f64 | container.Vector[scalar.i64],
) -> scalar.i64 | scalar.f64:
    """
    Find the maximum value in a scalar or vector.

    For a scalar, this will return the scalar itself.
    For a vector, this will find the maximum value of all elements.

    Args:
        x: Value to find maximum of

    Returns:
        Maximum value as a scalar (same type as input for scalars, i64 for i64 vectors)

    Raises:
        ValueError: If the input vector is not of type i64
        TypeError: If there's an error during the maximum calculation
    """
    if isinstance(x, container.Vector):
        if x.class_type == scalar.f64:
            raise ValueError("F64 vectors are not supported for maximum operation")
        elif x.class_type != scalar.i64:
            raise ValueError("Vector must be of type i64")

    elif not isinstance(x, (scalar.i64, scalar.f64)):
        raise ValueError(
            "Input must be a scalar of type i64 or f64, or a vector of type i64"
        )

    try:
        ptr = getattr(r.RayObject, ray_max_method)(x.ptr)
    except Exception as e:
        raise TypeError(f"Error when calling {ray_max_method} - {str(e)}")

    return container.from_pointer_to_raypy_type(ptr)
