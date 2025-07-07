from raypy import _rayforce as r
from raypy.api.exceptions import c_api_exception_handler


@c_api_exception_handler
def is_vector(ptr: r.RayObject) -> bool:
    return r.is_vector(ptr)


@c_api_exception_handler
def get_obj_length(ptr: r.RayObject) -> int:
    return r.get_obj_length(ptr)


@c_api_exception_handler
def get_error_message(ptr: r.RayObject) -> str:
    return r.get_error_message(ptr)


@c_api_exception_handler
def binary_set(name: r.RayObject, ptr: r.RayObject) -> None:
    r.binary_set(name, ptr)


@c_api_exception_handler
def env_get_internal_function_by_name(name: r.RayObject) -> r.RayObject:
    return r.env_get_internal_function_by_name(name)


@c_api_exception_handler
def env_get_internal_name_by_function(obj: r.RayObject) -> str:
    return r.env_get_internal_name_by_function(obj)


@c_api_exception_handler
def set_obj_attrs(ptr: r.RayObject, attrs: int) -> None:
    r.set_obj_attrs(ptr, attrs)


@c_api_exception_handler
def eval_obj(ptr: r.RayObject) -> r.RayObject:
    return r.eval_obj(ptr)


@c_api_exception_handler
def eval_str(query: str) -> r.RayObject:
    return r.eval_str(query)


@c_api_exception_handler
def loadfn_from_file(filename: str, fn_name: str, args_count: int) -> r.RayObject:
    return r.loadfn_from_file(filename, fn_name, args_count)
