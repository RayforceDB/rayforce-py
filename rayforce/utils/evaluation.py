from __future__ import annotations

import typing as t

from rayforce import _rayforce_c as r
from rayforce.core.ffi import FFI
from rayforce.types import exceptions
from rayforce.utils.conversion import ray_to_python


def eval_str(expr: str) -> t.Any:
    if not isinstance(expr, str):
        raise exceptions.RayEvaluationError(f"Expression must be a string, got {type(expr)}")

    result_ptr = FFI.eval_str(FFI.init_string(expr))
    if result_ptr.get_obj_type() == r.TYPE_ERR:
        raise exceptions.RayEvaluationError(
            f"Evaluation error: {FFI.get_error_message(result_ptr)}"
        )

    return ray_to_python(result_ptr)


def eval_obj(obj: t.Any) -> t.Any:
    if hasattr(obj, "ptr"):
        ptr = obj.ptr
    elif isinstance(obj, r.RayObject):
        ptr = obj
    else:
        raise exceptions.RayEvaluationError(f"Cannot evaluate {type(obj)}")

    result_ptr = FFI.eval_obj(ptr)
    if result_ptr.get_obj_type() == r.TYPE_ERR:
        raise exceptions.RayEvaluationError(
            f"Evaluation error: {FFI.get_error_message(result_ptr)}"
        )

    return ray_to_python(result_ptr)
