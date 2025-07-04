import typing as t

from raypy.api.exceptions import c_api_exception_handler
from raypy import _rayforce as r


@c_api_exception_handler
def init_b8(value: t.Any) -> r.RayObject:
    return r.init_b8(value)


@c_api_exception_handler
def init_c8(value: t.Any) -> r.RayObject:
    return r.init_c8(value)


@c_api_exception_handler
def init_date(value: t.Any) -> r.RayObject:
    return r.init_date(value)


@c_api_exception_handler
def init_f64(value: t.Any) -> r.RayObject:
    return r.init_f64(value)


@c_api_exception_handler
def init_i16(value: t.Any) -> r.RayObject:
    return r.init_i16(value)


@c_api_exception_handler
def init_i32(value: t.Any) -> r.RayObject:
    return r.init_i32(value)


@c_api_exception_handler
def init_i64(value: t.Any) -> r.RayObject:
    return r.init_i64(value)


@c_api_exception_handler
def init_symbol(value: t.Any) -> r.RayObject:
    return r.init_symbol(value)


@c_api_exception_handler
def init_time(value: t.Any) -> r.RayObject:
    return r.init_time(value)


@c_api_exception_handler
def init_timestamp(value: t.Any) -> r.RayObject:
    return r.init_timestamp(value)


@c_api_exception_handler
def init_u8(value: t.Any) -> r.RayObject:
    return r.init_u8(value)
