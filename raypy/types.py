from . import rayforce
from .obj import RayforceObject


def b8(value: bool) -> RayforceObject:
    """
    Create a boolean atom.

    Args:
        value: Python boolean value

    Returns:
        RayforceObject representing a boolean
    """
    return RayforceObject(rayforce.b8(bool(value)))


def i16(value: int) -> RayforceObject:
    """
    Create a 16-bit integer atom.

    Args:
        value: Python integer value

    Returns:
        RayforceObject representing a 16-bit integer
    """
    return RayforceObject(rayforce.i16(value))


def i32(value: int) -> RayforceObject:
    """
    Create a 32-bit integer atom.

    Args:
        value: Python integer value

    Returns:
        RayforceObject representing a 32-bit integer
    """
    return RayforceObject(rayforce.i32(value))


def i64(value: int) -> RayforceObject:
    """
    Create a 64-bit integer atom.

    Args:
        value: Python integer value

    Returns:
        RayforceObject representing a 64-bit integer
    """
    return RayforceObject(rayforce.i64(value))


def f64(value: float) -> RayforceObject:
    """
    Create a double-precision floating point atom.

    Args:
        value: Python float value

    Returns:
        RayforceObject representing a double-precision float
    """
    return RayforceObject(rayforce.f64(value))
