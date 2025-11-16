from __future__ import annotations
import typing as t
from functools import wraps

from raypy import _rayforce as r


def exception_handler(func: t.Callable) -> t.Callable:
    """
    Decorator to handle exceptions from C API calls.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, r.RayObject):
            obj_type = result.get_obj_type()
            # Check if result is an error object
            if obj_type == r.TYPE_ERR:
                error_msg = FFI.get_error_message(result)
                raise Exception(f"C API error: {error_msg}")
        return result

    return wrapper


class FFI:
    """
    Foreign Function Interface to the C API.
    """

    @staticmethod
    @exception_handler
    def init_i16(value: int) -> r.RayObject:
        return r.init_i16(value)

    @staticmethod
    @exception_handler
    def init_i32(value: int) -> r.RayObject:
        return r.init_i32(value)

    @staticmethod
    @exception_handler
    def init_i64(value: int) -> r.RayObject:
        return r.init_i64(value)

    @staticmethod
    @exception_handler
    def init_f64(value: float) -> r.RayObject:
        return r.init_f64(value)

    @staticmethod
    @exception_handler
    def init_u8(value: int) -> r.RayObject:
        return r.init_u8(value)

    @staticmethod
    @exception_handler
    def init_b8(value: bool) -> r.RayObject:
        return r.init_b8(value)

    @staticmethod
    @exception_handler
    def init_c8(value: str) -> r.RayObject:
        return r.init_c8(value)

    @staticmethod
    @exception_handler
    def init_symbol(value: str) -> r.RayObject:
        return r.init_symbol(value)

    @staticmethod
    @exception_handler
    def init_date(value: t.Any) -> r.RayObject:
        return r.init_date(value)

    @staticmethod
    @exception_handler
    def init_time(value: t.Any) -> r.RayObject:
        return r.init_time(value)

    @staticmethod
    @exception_handler
    def init_timestamp(value: t.Any) -> r.RayObject:
        return r.init_timestamp(value)

    @staticmethod
    @exception_handler
    def init_guid(value: t.Any) -> r.RayObject:
        return r.init_guid(value)

    @staticmethod
    @exception_handler
    def init_string(value: str) -> r.RayObject:
        return r.init_string(value)

    @staticmethod
    @exception_handler
    def read_i16(obj: r.RayObject) -> int:
        return r.read_i16(obj)

    @staticmethod
    @exception_handler
    def read_i32(obj: r.RayObject) -> int:
        return r.read_i32(obj)

    @staticmethod
    @exception_handler
    def read_i64(obj: r.RayObject) -> int:
        return r.read_i64(obj)

    @staticmethod
    @exception_handler
    def read_f64(obj: r.RayObject) -> float:
        return r.read_f64(obj)

    @staticmethod
    @exception_handler
    def read_u8(obj: r.RayObject) -> int:
        return r.read_u8(obj)

    @staticmethod
    @exception_handler
    def read_b8(obj: r.RayObject) -> bool:
        return r.read_b8(obj)

    @staticmethod
    @exception_handler
    def read_c8(obj: r.RayObject) -> str:
        return r.read_c8(obj)

    @staticmethod
    @exception_handler
    def read_symbol(obj: r.RayObject) -> str:
        return r.read_symbol(obj)

    @staticmethod
    @exception_handler
    def read_date(obj: r.RayObject) -> t.Any:
        return r.read_date(obj)

    @staticmethod
    @exception_handler
    def read_time(obj: r.RayObject) -> t.Any:
        return r.read_time(obj)

    @staticmethod
    @exception_handler
    def read_timestamp(obj: r.RayObject) -> t.Any:
        return r.read_timestamp(obj)

    @staticmethod
    @exception_handler
    def read_guid(obj: r.RayObject) -> t.Any:
        return r.read_guid(obj)

    @staticmethod
    @exception_handler
    def init_vector(type_code: int, length: int) -> r.RayObject:
        return r.init_vector(type_code, length)

    @staticmethod
    @exception_handler
    def init_list() -> r.RayObject:
        return r.init_list()

    @staticmethod
    @exception_handler
    def init_dict(keys: r.RayObject, values: r.RayObject) -> r.RayObject:
        return r.init_dict(keys, values)

    @staticmethod
    @exception_handler
    def init_table(columns: r.RayObject, values: r.RayObject) -> r.RayObject:
        return r.init_table(columns, values)

    @staticmethod
    @exception_handler
    def push_obj(iterable: r.RayObject, ptr: r.RayObject) -> None:
        return r.push_obj(iterable, ptr)

    @staticmethod
    @exception_handler
    def insert_obj(insert_to: r.RayObject, idx: int, ptr: r.RayObject) -> None:
        return r.insert_obj(insert_to, idx, ptr)

    @staticmethod
    @exception_handler
    def at_idx(obj: r.RayObject, idx: int) -> r.RayObject:
        return r.at_idx(obj, idx)

    @staticmethod
    @exception_handler
    def get_obj_length(obj: r.RayObject) -> int:
        return r.get_obj_length(obj)

    @staticmethod
    @exception_handler
    def is_vector(obj: r.RayObject) -> bool:
        return r.is_vector(obj)

    @staticmethod
    @exception_handler
    def get_table_keys(table: r.RayObject) -> r.RayObject:
        return r.table_keys(table)

    @staticmethod
    @exception_handler
    def get_table_values(table: r.RayObject) -> r.RayObject:
        return r.table_values(table)

    @staticmethod
    @exception_handler
    def repr_table(table: r.RayObject) -> str:
        return r.repr_table(table)

    @staticmethod
    @exception_handler
    def dict_get(dictionary: r.RayObject, key: r.RayObject) -> r.RayObject:
        return r.dict_get(dictionary, key)

    @staticmethod
    @exception_handler
    def get_dict_keys(dictionary: r.RayObject) -> r.RayObject:
        return r.dict_keys(dictionary)

    @staticmethod
    @exception_handler
    def get_dict_values(dictionary: r.RayObject) -> r.RayObject:
        return r.dict_values(dictionary)

    @staticmethod
    @exception_handler
    def select(query: r.RayObject) -> r.RayObject:
        return r.select(query)

    @staticmethod
    @exception_handler
    def update(query: r.RayObject) -> r.RayObject:
        return r.update(query)

    @staticmethod
    @exception_handler
    def insert(
        table_obj: r.RayObject,
        data_obj: r.RayObject,
    ) -> r.RayObject:
        return r.insert(table_obj, data_obj)

    @staticmethod
    @exception_handler
    def upsert(
        table_obj: r.RayObject,
        keys_obj: r.RayObject,
        data_obj: r.RayObject,
    ) -> r.RayObject:
        return r.upsert(table_obj, keys_obj, data_obj)

    @staticmethod
    @exception_handler
    def eval_str(expr: r.RayObject) -> r.RayObject:
        return r.eval_str(expr)

    @staticmethod
    @exception_handler
    def eval_obj(obj: r.RayObject) -> r.RayObject:
        return r.eval_obj(obj)

    @staticmethod
    @exception_handler
    def binary_set(name: r.RayObject, value: r.RayObject) -> None:
        return r.binary_set(name, value)

    @staticmethod
    @exception_handler
    def env_get_internal_function_by_name(name: str) -> r.RayObject:
        return r.env_get_internal_function_by_name(name)

    @staticmethod
    @exception_handler
    def env_get_internal_name_by_function(func: r.RayObject) -> str:
        return r.env_get_internal_name_by_function(func)

    @staticmethod
    @exception_handler
    def set_obj_attrs(obj: r.RayObject, attrs: r.RayObject) -> None:
        return r.set_obj_attrs(obj, attrs)

    @staticmethod
    @exception_handler
    def loadfn_from_file(filename: str) -> r.RayObject:
        return r.loadfn_from_file(filename)

    @staticmethod
    def get_error_message(error_obj: r.RayObject) -> str:
        try:
            return r.get_error_message(error_obj)
        except Exception:
            return "Unknown error"

    @staticmethod
    @exception_handler
    def hopen(host: str, port: int) -> r.RayObject:
        return r.hopen(host, port)

    @staticmethod
    @exception_handler
    def hclose(handle: r.RayObject) -> None:
        return r.hclose(handle)

    @staticmethod
    @exception_handler
    def write(handle: r.RayObject, data: r.RayObject) -> None:
        return r.write(handle, data)
