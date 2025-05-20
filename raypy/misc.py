from raypy import _rayforce as r


def eval_str(expr: str) -> r.RayObject:
    """
    Evaluate a Rayforce expression string.
    """
    if not isinstance(expr, str):
        raise TypeError("Expression must be a string")

    str_obj = r.RayObject.from_string(expr)
    if str_obj is None:
        raise ValueError("Failed to create string object")

    result = str_obj.ray_eval()
    if result is None:
        raise ValueError("Failed to evaluate expression")

    if result.get_type() == r.TYPE_ERR:
        error_message = result.get_error_message()
        raise Exception(f"Eval error: {error_message}")

    return result
