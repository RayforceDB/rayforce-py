from __future__ import annotations

import functools
import threading
import typing as t

from rayforce import _rayforce_c as r
from rayforce import errors

_main_thread_id: int | None = None


def thread_safety(func: t.Callable) -> t.Callable:
    @errors.error_handler
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global _main_thread_id  # noqa: PLW0602
        if _main_thread_id is None:
            raise errors.RayforceThreadError("Runtime not initialized.")
        if threading.get_ident() != _main_thread_id:
            raise errors.RayforceThreadError(
                "Rayforce can't be called within thread other than the one"
                f"where it was initialized (thread {_main_thread_id})"
            )
        return func(*args, **kwargs)

    return wrapper


class FFI:
    @staticmethod
    @thread_safety
    def init_i16(value: int) -> r.RayObject:
        return r.init_i16(value)

    @staticmethod
    @thread_safety
    def init_i32(value: int) -> r.RayObject:
        return r.init_i32(value)

    @staticmethod
    @thread_safety
    def init_i64(value: int) -> r.RayObject:
        return r.init_i64(value)

    @staticmethod
    @thread_safety
    def init_f64(value: float) -> r.RayObject:
        return r.init_f64(value)

    @staticmethod
    @thread_safety
    def init_u8(value: int) -> r.RayObject:
        return r.init_u8(value)

    @staticmethod
    @thread_safety
    def init_b8(value: bool) -> r.RayObject:
        return r.init_b8(value)

    @staticmethod
    @thread_safety
    def init_c8(value: str) -> r.RayObject:
        return r.init_c8(value)

    @staticmethod
    @thread_safety
    def init_symbol(value: str) -> r.RayObject:
        return r.init_symbol(value)

    @staticmethod
    @thread_safety
    def init_date(value: t.Any) -> r.RayObject:
        return r.init_date(value)

    @staticmethod
    @thread_safety
    def init_time(value: t.Any) -> r.RayObject:
        return r.init_time(value)

    @staticmethod
    @thread_safety
    def init_timestamp(value: t.Any) -> r.RayObject:
        return r.init_timestamp(value)

    @staticmethod
    @thread_safety
    def init_guid(value: t.Any) -> r.RayObject:
        return r.init_guid(value)

    @staticmethod
    @thread_safety
    def init_string(value: str) -> r.RayObject:
        return r.init_string(value)

    @staticmethod
    @thread_safety
    def read_i16(obj: r.RayObject) -> int:
        return r.read_i16(obj)

    @staticmethod
    @thread_safety
    def read_i32(obj: r.RayObject) -> int:
        return r.read_i32(obj)

    @staticmethod
    @thread_safety
    def read_i64(obj: r.RayObject) -> int:
        return r.read_i64(obj)

    @staticmethod
    @thread_safety
    def read_f64(obj: r.RayObject) -> float:
        return r.read_f64(obj)

    @staticmethod
    @thread_safety
    def read_u8(obj: r.RayObject) -> int:
        return r.read_u8(obj)

    @staticmethod
    @thread_safety
    def read_b8(obj: r.RayObject) -> bool:
        return r.read_b8(obj)

    @staticmethod
    @thread_safety
    def read_c8(obj: r.RayObject) -> str:
        return r.read_c8(obj)

    @staticmethod
    @thread_safety
    def read_symbol(obj: r.RayObject) -> str:
        return r.read_symbol(obj)

    @staticmethod
    @thread_safety
    def read_date(obj: r.RayObject) -> t.Any:
        return r.read_date(obj)

    @staticmethod
    @thread_safety
    def read_time(obj: r.RayObject) -> t.Any:
        return r.read_time(obj)

    @staticmethod
    @thread_safety
    def read_timestamp(obj: r.RayObject) -> t.Any:
        return r.read_timestamp(obj)

    @staticmethod
    @thread_safety
    def read_guid(obj: r.RayObject) -> t.Any:
        return r.read_guid(obj)

    @staticmethod
    @thread_safety
    def init_vector(type_code: int, length: int) -> r.RayObject:
        return r.init_vector(type_code, length)

    @staticmethod
    @thread_safety
    def init_list() -> r.RayObject:
        return r.init_list()

    @staticmethod
    @thread_safety
    def init_dict(keys: r.RayObject, values: r.RayObject) -> r.RayObject:
        return r.init_dict(keys, values)

    @staticmethod
    @thread_safety
    def init_table(columns: r.RayObject, values: r.RayObject) -> r.RayObject:
        return r.init_table(columns, values)

    @staticmethod
    @thread_safety
    def push_obj(iterable: r.RayObject, ptr: r.RayObject) -> None:
        return r.push_obj(iterable, ptr)

    @staticmethod
    @thread_safety
    def insert_obj(iterable: r.RayObject, idx: int, ptr: r.RayObject) -> None:
        return r.insert_obj(iterable, idx, ptr)

    @staticmethod
    @thread_safety
    def fill_vector(obj: r.RayObject, fill: list[t.Any]) -> None:
        return r.fill_vector(obj, fill)

    @staticmethod
    @thread_safety
    def fill_list(obj: r.RayObject, fill: list[t.Any]) -> None:
        return r.fill_list(obj, fill)

    @staticmethod
    @thread_safety
    def at_idx(iterable: r.RayObject, idx: int) -> r.RayObject:
        return r.at_idx(iterable, idx)

    @staticmethod
    @thread_safety
    def get_obj_length(obj: r.RayObject) -> int:
        return r.get_obj_length(obj)

    @staticmethod
    @thread_safety
    def get_table_keys(table: r.RayObject) -> r.RayObject:
        return r.table_keys(table)

    @staticmethod
    @thread_safety
    def get_table_values(table: r.RayObject) -> r.RayObject:
        return r.table_values(table)

    @staticmethod
    @thread_safety
    def repr_table(table: r.RayObject) -> str:
        return r.repr_table(table)

    @staticmethod
    @thread_safety
    def dict_get(dict_: r.RayObject, key: r.RayObject) -> r.RayObject:
        return r.dict_get(dict_, key)

    @staticmethod
    @thread_safety
    def get_dict_keys(dict_: r.RayObject) -> r.RayObject:
        return r.dict_keys(dict_)

    @staticmethod
    @thread_safety
    def get_dict_values(dict_: r.RayObject) -> r.RayObject:
        return r.dict_values(dict_)

    @staticmethod
    @thread_safety
    def select(query: r.RayObject) -> r.RayObject:
        return r.select(query)

    @staticmethod
    @thread_safety
    def update(query: r.RayObject) -> r.RayObject:
        return r.update(query)

    @staticmethod
    @thread_safety
    def insert(table: r.RayObject, data: r.RayObject) -> r.RayObject:
        return r.insert(table, data)

    @staticmethod
    @thread_safety
    def upsert(table: r.RayObject, keys: r.RayObject, data: r.RayObject) -> r.RayObject:
        return r.upsert(table, keys, data)

    @staticmethod
    @thread_safety
    def eval_str(obj: r.RayObject) -> r.RayObject:
        return r.eval_str(obj)

    @staticmethod
    @thread_safety
    def eval_obj(obj: r.RayObject) -> r.RayObject:
        return r.eval_obj(obj)

    @staticmethod
    @thread_safety
    def quote(obj: r.RayObject) -> r.RayObject:
        return r.quote(obj)

    @staticmethod
    @thread_safety
    def rc_obj(obj: r.RayObject) -> int:
        return r.rc_obj(obj)

    @staticmethod
    @thread_safety
    def binary_set(name: r.RayObject, obj: r.RayObject) -> None:
        return r.binary_set(name, obj)

    @staticmethod
    @thread_safety
    def env_get_internal_function_by_name(name: str) -> r.RayObject:
        return r.env_get_internal_function_by_name(name)

    @staticmethod
    @thread_safety
    def env_get_internal_name_by_function(obj: r.RayObject) -> str:
        return r.env_get_internal_name_by_function(obj)

    @staticmethod
    @thread_safety
    def set_obj_attrs(obj: r.RayObject, attr: int) -> None:
        return r.set_obj_attrs(obj, attr)

    @staticmethod
    @thread_safety
    def loadfn_from_file(filename: str, fn_name: str, args_count: int) -> r.RayObject:
        return r.loadfn_from_file(filename, fn_name, args_count)

    @staticmethod
    @thread_safety
    def get_error_obj(error_obj: r.RayObject) -> r.RayObject:
        return r.get_error_obj(error_obj)

    @staticmethod
    @thread_safety
    def hopen(path: r.RayObject) -> r.RayObject:
        return r.hopen(path)

    @staticmethod
    @thread_safety
    def hclose(handle: r.RayObject) -> None:
        return r.hclose(handle)

    @staticmethod
    @thread_safety
    def write(handle: r.RayObject, data: r.RayObject) -> None:
        return r.write(handle, data)

    @staticmethod
    @thread_safety
    def set_obj(obj: r.RayObject, idx: r.RayObject, value: r.RayObject) -> None:
        return r.set_obj(obj, idx, value)

    @staticmethod
    @errors.error_handler
    def init_runtime() -> None:
        r.init_runtime()
        global _main_thread_id  # noqa: PLW0603
        _main_thread_id = threading.get_ident()

    @staticmethod
    @thread_safety
    def get_obj_type(obj: r.RayObject) -> int:
        return r.get_obj_type(obj)
