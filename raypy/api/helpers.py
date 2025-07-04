
from raypy import _rayforce as r
from raypy.api.exceptions import c_api_exception_handler


@c_api_exception_handler
def is_vector(ptr: r.RayObject) -> bool:
    return r.is_vector(ptr)


@c_api_exception_handler
def get_obj_length(ptr: r.RayObject) -> int:
    return r.get_obj_length(ptr)
