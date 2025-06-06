from raypy import _rayforce as r
from raypy.types import container as c


def eval_str(expr: str) -> r.RayObject:
    """
    Evaluate a Rayforce expression string.
    """
    if not isinstance(expr, str):
        raise TypeError("Expression must be a string")

    str_obj = r.init_string(expr)
    if str_obj is None:
        raise ValueError("Failed to create string object")

    result = r.eval_str(str_obj)
    if result is None:
        raise ValueError("Failed to evaluate expression")

    if result.get_obj_type() == r.TYPE_ERR:
        error_message = r.get_error_message(result)
        if error_message:
            raise ValueError(f"Evaluation error: {error_message}")
        raise ValueError(f"Evaluation error (type {result.get_obj_type()})")

    return c.from_pointer_to_raypy_type(result, return_raw=True)
