from raypy import _rayforce as r
from raypy import types as t
from raypy.core import FFI


def eval_str(expr: str) -> r.RayObject:
    """
    Evaluate a Rayforce expression string.
    """
    if not isinstance(expr, str):
        raise TypeError("Expression must be a string")

    str_obj = FFI.init_string(expr)
    if str_obj is None:
        raise ValueError("Failed to create string object")

    result = FFI.eval_str(str_obj)
    if result is None:
        raise ValueError("Failed to evaluate expression")

    if result.get_obj_type() == r.TYPE_ERR:
        error_message = FFI.get_error_message(result)
        if error_message:
            raise ValueError(f"Evaluation error: {error_message}")
        raise ValueError(f"Evaluation error (type {result.get_obj_type()})")

    return t.convert_raw_rayobject_to_raypy_type(result)


def eval_obj(obj: t.Any) -> t.Any:
    _obj = getattr(obj, "ptr", obj)
    result = FFI.eval_obj(_obj)
    return t.convert_raw_rayobject_to_raypy_type(result)


def set_table_name(name: str, table: t.Table) -> None:
    FFI.binary_set(FFI.init_symbol(name), table.ptr)


def set_var_name(name: str, var: t.Any) -> None:
    FFI.binary_set(FFI.init_symbol(name), var.ptr)


def set_lambda_name(name: str, _lambda: t.Lambda) -> None:  # type: ignore
    FFI.binary_set(FFI.init_symbol(name), _lambda.ptr)
