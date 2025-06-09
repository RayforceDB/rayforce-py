from typing import Any

from raypy import api
from raypy import _rayforce as r
from raypy import types as t


def lambda_call(_lambda: t.Lambda, *args) -> Any:
    result_ptr = api.lambda_call(
        _lambda.ptr, *[api.from_python_to_rayforce_type(arg) for arg in args]
    )

    if result_ptr.get_obj_type() == r.TYPE_ERR:
        raise ValueError(f"Query error: {api.get_error_message(result_ptr)}")

    return t.from_rf_to_raypy(result_ptr)
