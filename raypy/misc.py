from raypy import _rayforce as r
from raypy import api
from raypy import types as t


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

    return t.from_rf_to_raypy(result)


def set_table_name(name: str, table: t.Table) -> None:
    api.set_obj_to_env(name, table.ptr)
