import typing as t

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


@c_api_exception_handler
def read_guid(ptr: r.RayObject) -> bytes:
    return r.read_guid(ptr)


@c_api_exception_handler
def at_idx(get_from: r.RayObject, idx: int) -> r.RayObject:
    return r.at_idx(get_from, idx)


@c_api_exception_handler
def dict_get(dict: r.RayObject, key: t.Any) -> r.RayObject:
    return r.dict_get(dict, key)


@c_api_exception_handler
def get_table_keys(table_ptr: r.RayObject) -> r.RayObject:
    return r.table_keys(table_ptr)


@c_api_exception_handler
def get_table_values(table_ptr: r.RayObject) -> r.RayObject:
    return r.table_values(table_ptr)


@c_api_exception_handler
def get_dict_keys(ptr: r.RayObject) -> r.RayObject:
    return r.dict_keys(ptr)


@c_api_exception_handler
def get_dict_values(ptr: r.RayObject) -> r.RayObject:
    return r.dict_values(ptr)
