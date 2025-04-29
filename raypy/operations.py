from . import rayforce
from .types import RayforceObject

_INTEGER_UNICODE_SURROGATE = "\udcfb"
_FLOAT_UNICODE_SURROGATE = "\udcf6"


def __list_add_scalar(*, li: list, scalar: int | float) -> list:
    """Add a scalar to each element in a list."""
    return [add(item, scalar) for item in li]


def __list_sub_scalar(*, li: list, scalar: int | float) -> list:
    """Subtract a scalar from each element in a list."""
    return [sub(item, scalar) for item in li]


def __scalar_sub_list(*, scalar: int | float, li: list) -> list:
    """Subtract each list element from a scalar."""
    return [sub(scalar, item) for item in li]


def __list_mul_scalar(*, li: list, scalar: int | float) -> list:
    """Multiply each element in a list by a scalar."""
    return [mul(item, scalar) for item in li]


def __list_fdiv_scalar(*, li: list, scalar: int | float) -> list:
    """Divide each element in a list by a scalar."""
    return [fdiv(item, scalar) for item in li]


def __scalar_fdiv_list(*, scalar: int | float, li: list) -> list:
    """Divide a scalar by each element in a list."""
    return [fdiv(scalar, item) for item in li]


def __list_div_scalar(*, li: list, scalar: int | float) -> list:
    """Perform integer division on each element in a list by a scalar."""
    return [div(item, scalar) for item in li]


def __scalar_div_list(*, scalar: int | float, li: list) -> list:
    """Perform integer division of a scalar by each element in a list."""
    return [div(scalar, item) for item in li]


def add(
    x: int | float | list[int | float] | RayforceObject,
    y: int | float | list[int | float] | RayforceObject,
) -> int | float | list[int | float]:
    """
    Add two values.
    Handles integers, floats, and lists.

    Returns:
        - int | float | list result of an addition.
    """

    if isinstance(x, list):
        if isinstance(y, (int, float)):
            # Handle adding a scalar to each element of the X list
            return __list_add_scalar(li=x, scalar=y)
        elif isinstance(y, list):
            # Handle adding two lists
            if len(x) != len(y):
                raise ValueError(
                    f"Lists must have the same length for addition: {len(x)} != {len(y)}"
                )
            return [add(x[i], y[i]) for i in range(len(x))]

    elif isinstance(y, list):
        # Handle adding a scalar to each element of the Y list
        if isinstance(x, (int, float)):
            return __list_add_scalar(li=y, scalar=x)

    if isinstance(x, RayforceObject):
        x_obj = x.obj
    elif isinstance(x, int):
        x_obj = rayforce.i64(x)
    elif isinstance(x, float):
        x_obj = rayforce.f64(x)
    else:
        raise TypeError(
            f"Expected int, float, list, or RayforceObject, got {type(x).__name__}"
        )

    if isinstance(y, RayforceObject):
        y_obj = y.obj
    elif isinstance(y, int):
        y_obj = rayforce.i64(y)
    elif isinstance(y, float):
        y_obj = rayforce.f64(y)
    else:
        raise TypeError(
            f"Expected int, float, list, or RayforceObject, got {type(y).__name__}"
        )

    result_obj = rayforce.ray_add(x_obj, y_obj)

    if hasattr(result_obj, "type"):
        # Integer results
        if result_obj.type == _INTEGER_UNICODE_SURROGATE and hasattr(result_obj, "i64"):
            return result_obj.i64
        elif isinstance(result_obj.type, int) and result_obj.type == -rayforce.TYPE_I64:
            return result_obj.i64
        # Float results
        elif result_obj.type == _FLOAT_UNICODE_SURROGATE and hasattr(result_obj, "f64"):
            return result_obj.f64
        elif isinstance(result_obj.type, int) and result_obj.type == -rayforce.TYPE_F64:
            return result_obj.f64

    raise ValueError(
        f"Could not convert result to int or float (type: {getattr(result_obj, 'type', 'unknown')})"
    )


def sub(
    x: int | float | list[int | float] | RayforceObject,
    y: int | float | list[int | float] | RayforceObject,
) -> int | float | list[int | float]:
    """
    Substract y from x.
    Handles integers, floats, and lists.

    Returns:
        - int | float | list result of a subtraction.
    """

    if isinstance(x, list):
        if isinstance(y, (int, float)):
            # Handle subtracting a scalar from each element of the X list
            return __list_sub_scalar(li=x, scalar=y)
        elif isinstance(y, list):
            # Handle subtracting two lists
            if len(x) != len(y):
                raise ValueError(
                    f"Lists must have the same length for subtraction: {len(x)} != {len(y)}"
                )
            return [sub(x[i], y[i]) for i in range(len(x))]

    elif isinstance(y, list):
        # Handle subtracting a list from a scalar
        if isinstance(x, (int, float)):
            return __scalar_sub_list(scalar=x, li=y)

    if isinstance(x, RayforceObject):
        x_obj = x.obj
    elif isinstance(x, int):
        x_obj = rayforce.i64(x)
    elif isinstance(x, float):
        x_obj = rayforce.f64(x)
    else:
        raise TypeError(
            f"Expected int, float, list, or RayforceObject, got {type(x).__name__}"
        )

    if isinstance(y, RayforceObject):
        y_obj = y.obj
    elif isinstance(y, int):
        y_obj = rayforce.i64(y)
    elif isinstance(y, float):
        y_obj = rayforce.f64(y)
    else:
        raise TypeError(
            f"Expected int, float, list, or RayforceObject, got {type(y).__name__}"
        )

    result_obj = rayforce.ray_sub(x_obj, y_obj)

    if hasattr(result_obj, "type"):
        # Integer results
        if result_obj.type == _INTEGER_UNICODE_SURROGATE and hasattr(result_obj, "i64"):
            return result_obj.i64
        elif isinstance(result_obj.type, int) and result_obj.type == -rayforce.TYPE_I64:
            return result_obj.i64

        # Float results
        elif result_obj.type == _FLOAT_UNICODE_SURROGATE and hasattr(result_obj, "f64"):
            return result_obj.f64
        elif isinstance(result_obj.type, int) and result_obj.type == -rayforce.TYPE_F64:
            return result_obj.f64

    raise ValueError(
        f"Could not convert result to int or float (type: {getattr(result_obj, 'type', 'unknown')})"
    )


def mul(
    x: int | float | list[int | float] | RayforceObject,
    y: int | float | list[int | float] | RayforceObject,
) -> int | float | list[int | float]:
    """
    Multiply two values.
    Handles integers, floats, and lists.

    Returns:
        - int | float | list result of a multiplication.
    """

    if isinstance(x, list):
        if isinstance(y, (int, float)):
            # Handle multiplying each element of the X list by a scalar
            return __list_mul_scalar(li=x, scalar=y)
        elif isinstance(y, list):
            # Handle element-wise multiplication of two lists
            if len(x) != len(y):
                raise ValueError(
                    f"Lists must have the same length for multiplication: {len(x)} != {len(y)}"
                )
            return [mul(x[i], y[i]) for i in range(len(x))]

    elif isinstance(y, list):
        # Handle multiplying each element of the Y list by a scalar
        if isinstance(x, (int, float)):
            return __list_mul_scalar(li=y, scalar=x)

    if isinstance(x, RayforceObject):
        x_obj = x.obj
    elif isinstance(x, int):
        x_obj = rayforce.i64(x)
    elif isinstance(x, float):
        x_obj = rayforce.f64(x)
    else:
        raise TypeError(
            f"Expected int, float, list, or RayforceObject, got {type(x).__name__}"
        )

    if isinstance(y, RayforceObject):
        y_obj = y.obj
    elif isinstance(y, int):
        y_obj = rayforce.i64(y)
    elif isinstance(y, float):
        y_obj = rayforce.f64(y)
    else:
        raise TypeError(
            f"Expected int, float, list, or RayforceObject, got {type(y).__name__}"
        )

    result_obj = rayforce.ray_mul(x_obj, y_obj)

    if hasattr(result_obj, "type"):
        # Integer results
        if result_obj.type == _INTEGER_UNICODE_SURROGATE and hasattr(result_obj, "i64"):
            return result_obj.i64
        elif isinstance(result_obj.type, int) and result_obj.type == -rayforce.TYPE_I64:
            return result_obj.i64

        # Float results
        elif result_obj.type == _FLOAT_UNICODE_SURROGATE and hasattr(result_obj, "f64"):
            return result_obj.f64
        elif isinstance(result_obj.type, int) and result_obj.type == -rayforce.TYPE_F64:
            return result_obj.f64

    raise ValueError(
        f"Could not convert result to int or float (type: {getattr(result_obj, 'type', 'unknown')})"
    )


def fdiv(
    x: int | float | list[int | float] | RayforceObject,
    y: int | float | list[int | float] | RayforceObject,
) -> int | float | list[int | float]:
    """
    Divide x by y.
    Handles integers, floats, and lists.

    Returns:
        - int | float | list result of a division.
    """

    if isinstance(x, list):
        if isinstance(y, (int, float)):
            # Handle dividing each element of the X list by a scalar
            return __list_fdiv_scalar(li=x, scalar=y)
        elif isinstance(y, list):
            # Handle element-wise division of two lists
            if len(x) != len(y):
                raise ValueError(
                    f"Lists must have the same length for division: {len(x)} != {len(y)}"
                )
            return [fdiv(x[i], y[i]) for i in range(len(x))]

    elif isinstance(y, list):
        # Handle dividing a scalar by each element of the Y list
        if isinstance(x, (int, float)):
            return __scalar_fdiv_list(scalar=x, li=y)

    if isinstance(x, RayforceObject):
        x_obj = x.obj
    elif isinstance(x, int):
        x_obj = rayforce.i64(x)
    elif isinstance(x, float):
        x_obj = rayforce.f64(x)
    else:
        raise TypeError(
            f"Expected int, float, list, or RayforceObject, got {type(x).__name__}"
        )

    if isinstance(y, RayforceObject):
        y_obj = y.obj
    elif isinstance(y, int):
        y_obj = rayforce.i64(y)
    elif isinstance(y, float):
        y_obj = rayforce.f64(y)
    else:
        raise TypeError(
            f"Expected int, float, list, or RayforceObject, got {type(y).__name__}"
        )

    result_obj = rayforce.ray_fdiv(x_obj, y_obj)

    if hasattr(result_obj, "type"):
        # Integer results
        if result_obj.type == _INTEGER_UNICODE_SURROGATE and hasattr(result_obj, "i64"):
            return result_obj.i64
        elif isinstance(result_obj.type, int) and result_obj.type == -rayforce.TYPE_I64:
            return result_obj.i64

        # Float results
        elif result_obj.type == _FLOAT_UNICODE_SURROGATE and hasattr(result_obj, "f64"):
            return result_obj.f64
        elif isinstance(result_obj.type, int) and result_obj.type == -rayforce.TYPE_F64:
            return result_obj.f64

    raise ValueError(
        f"Could not convert result to int or float (type: {getattr(result_obj, 'type', 'unknown')})"
    )


def div(
    x: int | float | list[int | float] | RayforceObject,
    y: int | float | list[int | float] | RayforceObject,
) -> int | float | list[int | float]:
    """
    Perform integer division of x by y.
    Handles integers, floats, and lists.

    Returns:
        - int | float | list result of an integer division.
    """

    if isinstance(x, list):
        if isinstance(y, (int, float)):
            # Handle dividing each element of the X list by a scalar
            return __list_div_scalar(li=x, scalar=y)
        elif isinstance(y, list):
            # Handle element-wise division of two lists
            if len(x) != len(y):
                raise ValueError(
                    f"Lists must have the same length for division: {len(x)} != {len(y)}"
                )
            return [div(x[i], y[i]) for i in range(len(x))]

    elif isinstance(y, list):
        # Handle dividing a scalar by each element of the Y list
        if isinstance(x, (int, float)):
            return __scalar_div_list(scalar=x, li=y)

    if isinstance(x, RayforceObject):
        x_obj = x.obj
    elif isinstance(x, int):
        x_obj = rayforce.i64(x)
    elif isinstance(x, float):
        x_obj = rayforce.f64(x)
    else:
        raise TypeError(
            f"Expected int, float, list, or RayforceObject, got {type(x).__name__}"
        )

    if isinstance(y, RayforceObject):
        y_obj = y.obj
    elif isinstance(y, int):
        y_obj = rayforce.i64(y)
    elif isinstance(y, float):
        y_obj = rayforce.f64(y)
    else:
        raise TypeError(
            f"Expected int, float, list, or RayforceObject, got {type(y).__name__}"
        )

    result_obj = rayforce.ray_div(x_obj, y_obj)

    if hasattr(result_obj, "type"):
        # Integer results
        if result_obj.type == _INTEGER_UNICODE_SURROGATE and hasattr(result_obj, "i64"):
            return result_obj.i64
        elif isinstance(result_obj.type, int) and result_obj.type == -rayforce.TYPE_I64:
            return result_obj.i64

        # Float results
        elif result_obj.type == _FLOAT_UNICODE_SURROGATE and hasattr(result_obj, "f64"):
            return result_obj.f64
        elif isinstance(result_obj.type, int) and result_obj.type == -rayforce.TYPE_F64:
            return result_obj.f64

    raise ValueError(
        f"Could not convert result to int or float (type: {getattr(result_obj, 'type', 'unknown')})"
    )
