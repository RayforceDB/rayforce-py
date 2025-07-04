from raypy.api.exceptions import c_api_exception_handler
from raypy import _rayforce as r


@c_api_exception_handler
def read_b8(ptr: r.RayObject) -> bool:
    return r.read_b8(ptr)


@c_api_exception_handler
def read_c8(ptr: r.RayObject) -> str:
    return r.read_c8(ptr)


@c_api_exception_handler
def read_date(ptr: r.RayObject) -> int:
    return r.read_date(ptr)


@c_api_exception_handler
def read_f64(ptr: r.RayObject) -> float:
    return r.read_f64(ptr)


@c_api_exception_handler
def read_i16(ptr: r.RayObject) -> int:
    return r.read_i16(ptr)


@c_api_exception_handler
def read_i32(ptr: r.RayObject) -> int:
    return r.read_i32(ptr)


@c_api_exception_handler
def read_i64(ptr: r.RayObject) -> int:
    return r.read_i64(ptr)


@c_api_exception_handler
def read_symbol(ptr: r.RayObject) -> str:
    return r.read_symbol(ptr)


@c_api_exception_handler
def read_time(ptr: r.RayObject) -> int:
    return r.read_time(ptr)


@c_api_exception_handler
def read_timestamp(ptr: r.RayObject) -> int:
    return r.read_timestamp(ptr)


@c_api_exception_handler
def read_u8(ptr: r.RayObject) -> int:
    return r.read_u8(ptr)
