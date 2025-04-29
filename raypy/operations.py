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
