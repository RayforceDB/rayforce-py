from __future__ import annotations

import typing as t

from rayforce import _rayforce_c as r
from rayforce import errors


class FFI:
    @staticmethod
    @errors.error_handler
    def init_i16(value: int) -> r.RayObject:
        return r.init_i16(value)

    @staticmethod
    @errors.error_handler
    def init_i32(value: int) -> r.RayObject:
        return r.init_i32(value)

    @staticmethod
    @errors.error_handler
    def init_i64(value: int) -> r.RayObject:
        return r.init_i64(value)

    @staticmethod
    @errors.error_handler
    def init_f64(value: float) -> r.RayObject:
        return r.init_f64(value)

    @staticmethod
    @errors.error_handler
    def init_u8(value: int) -> r.RayObject:
        return r.init_u8(value)

    @staticmethod
    @errors.error_handler
    def init_b8(value: bool) -> r.RayObject:
        return r.init_b8(value)

    @staticmethod
    @errors.error_handler
    def init_c8(value: str) -> r.RayObject:
        return r.init_c8(value)

    @staticmethod
    @errors.error_handler
    def init_symbol(value: str) -> r.RayObject:
        return r.init_symbol(value)

    @staticmethod
    @errors.error_handler
    def init_date(value: t.Any) -> r.RayObject:
        return r.init_date(value)

    @staticmethod
    @errors.error_handler
    def init_time(value: t.Any) -> r.RayObject:
        return r.init_time(value)

    @staticmethod
    @errors.error_handler
    def init_timestamp(value: t.Any) -> r.RayObject:
        return r.init_timestamp(value)

    @staticmethod
    @errors.error_handler
    def init_guid(value: t.Any) -> r.RayObject:
        return r.init_guid(value)

    @staticmethod
    @errors.error_handler
    def init_string(value: str) -> r.RayObject:
        return r.init_string(value)

    @staticmethod
    @errors.error_handler
    def read_i16(obj: r.RayObject) -> int:
        return r.read_i16(obj)

    @staticmethod
    @errors.error_handler
    def read_i32(obj: r.RayObject) -> int:
        return r.read_i32(obj)

    @staticmethod
    @errors.error_handler
    def read_i64(obj: r.RayObject) -> int:
        return r.read_i64(obj)

    @staticmethod
    @errors.error_handler
    def read_f64(obj: r.RayObject) -> float:
        return r.read_f64(obj)

    @staticmethod
    @errors.error_handler
    def read_u8(obj: r.RayObject) -> int:
        return r.read_u8(obj)

    @staticmethod
    @errors.error_handler
    def read_b8(obj: r.RayObject) -> bool:
        return r.read_b8(obj)

    @staticmethod
    @errors.error_handler
    def read_c8(obj: r.RayObject) -> str:
        return r.read_c8(obj)

    @staticmethod
    @errors.error_handler
    def read_symbol(obj: r.RayObject) -> str:
        return r.read_symbol(obj)

    @staticmethod
    @errors.error_handler
    def read_date(obj: r.RayObject) -> t.Any:
        return r.read_date(obj)

    @staticmethod
    @errors.error_handler
    def read_time(obj: r.RayObject) -> t.Any:
        return r.read_time(obj)

    @staticmethod
    @errors.error_handler
    def read_timestamp(obj: r.RayObject) -> t.Any:
        return r.read_timestamp(obj)

    @staticmethod
    @errors.error_handler
    def read_guid(obj: r.RayObject) -> t.Any:
        return r.read_guid(obj)

    @staticmethod
    @errors.error_handler
    def init_vector(type_code: int, length: int) -> r.RayObject:
        return r.init_vector(type_code, length)

    @staticmethod
    @errors.error_handler
    def init_list() -> r.RayObject:
        return r.init_list()

    @staticmethod
    @errors.error_handler
    def init_dict(keys: r.RayObject, values: r.RayObject) -> r.RayObject:
        return r.init_dict(keys, values)

    @staticmethod
    @errors.error_handler
    def init_table(columns: r.RayObject, values: r.RayObject) -> r.RayObject:
        return r.init_table(columns, values)

    @staticmethod
    @errors.error_handler
    def push_obj(iterable: r.RayObject, ptr: r.RayObject) -> None:
        return r.push_obj(iterable, ptr)

    @staticmethod
    @errors.error_handler
    def insert_obj(iterable: r.RayObject, idx: int, ptr: r.RayObject) -> None:
        return r.insert_obj(iterable, idx, ptr)

    @staticmethod
    @errors.error_handler
    def fill_vector(obj: r.RayObject, fill: list[t.Any]) -> None:
        return r.fill_vector(obj, fill)

    @staticmethod
    @errors.error_handler
    def fill_list(obj: r.RayObject, fill: list[t.Any]) -> None:
        return r.fill_list(obj, fill)

    @staticmethod
    @errors.error_handler
    def at_idx(iterable: r.RayObject, idx: int) -> r.RayObject:
        return r.at_idx(iterable, idx)

    @staticmethod
    @errors.error_handler
    def get_obj_length(obj: r.RayObject) -> int:
        return r.get_obj_length(obj)

    @staticmethod
    @errors.error_handler
    def get_table_keys(table: r.RayObject) -> r.RayObject:
        return r.table_keys(table)

    @staticmethod
    @errors.error_handler
    def get_table_values(table: r.RayObject) -> r.RayObject:
        return r.table_values(table)

    @staticmethod
    @errors.error_handler
    def repr_table(table: r.RayObject) -> str:
        return r.repr_table(table)

    @staticmethod
    @errors.error_handler
    def dict_get(dict_: r.RayObject, key: r.RayObject) -> r.RayObject:
        return r.dict_get(dict_, key)

    @staticmethod
    @errors.error_handler
    def get_dict_keys(dict_: r.RayObject) -> r.RayObject:
        return r.dict_keys(dict_)

    @staticmethod
    @errors.error_handler
    def get_dict_values(dict_: r.RayObject) -> r.RayObject:
        return r.dict_values(dict_)

    @staticmethod
    @errors.error_handler
    def update(query: r.RayObject) -> r.RayObject:
        return r.update(query)

    @staticmethod
    @errors.error_handler
    def insert(table: r.RayObject, data: r.RayObject) -> r.RayObject:
        return r.insert(table, data)

    @staticmethod
    @errors.error_handler
    def upsert(table: r.RayObject, keys: r.RayObject, data: r.RayObject) -> r.RayObject:
        return r.upsert(table, keys, data)

    @staticmethod
    @errors.error_handler
    def eval_str(obj: r.RayObject) -> r.RayObject:
        return r.eval_str(obj)

    @staticmethod
    @errors.error_handler
    def eval_obj(obj: r.RayObject) -> r.RayObject:
        return r.eval_obj(obj)

    @staticmethod
    @errors.error_handler
    def quote(obj: r.RayObject) -> r.RayObject:
        return r.quote(obj)

    @staticmethod
    @errors.error_handler
    def rc_obj(obj: r.RayObject) -> int:
        return r.rc_obj(obj)

    @staticmethod
    @errors.error_handler
    def binary_set(name: r.RayObject, obj: r.RayObject) -> None:
        return r.binary_set(name, obj)

    @staticmethod
    @errors.error_handler
    def env_get_internal_fn_by_name(name: str) -> r.RayObject:
        return r.env_get_internal_fn_by_name(name)

    @staticmethod
    @errors.error_handler
    def env_get_internal_name_by_fn(obj: r.RayObject) -> str:
        return r.env_get_internal_name_by_fn(obj)

    @staticmethod
    @errors.error_handler
    def set_obj_attrs(obj: r.RayObject, attr: int) -> None:
        return r.set_obj_attrs(obj, attr)

    @staticmethod
    @errors.error_handler
    def loadfn_from_file(filename: str, fn_name: str, args_count: int) -> r.RayObject:
        return r.loadfn_from_file(filename, fn_name, args_count)

    @staticmethod
    @errors.error_handler
    def get_error_obj(error_obj: r.RayObject) -> r.RayObject:
        return r.get_error_obj(error_obj)

    @staticmethod
    @errors.error_handler
    def hopen(path: r.RayObject) -> r.RayObject:
        return r.hopen(path)

    @staticmethod
    @errors.error_handler
    def hclose(handle: r.RayObject) -> None:
        return r.hclose(handle)

    @staticmethod
    @errors.error_handler
    def write(handle: r.RayObject, data: r.RayObject) -> None:
        return r.write(handle, data)

    @staticmethod
    @errors.error_handler
    def set_obj(obj: r.RayObject, idx: r.RayObject, value: r.RayObject) -> None:
        return r.set_obj(obj, idx, value)

    @staticmethod
    @errors.error_handler
    def init_runtime() -> None:
        r.init_runtime()

    @staticmethod
    @errors.error_handler
    def get_obj_type(obj: r.RayObject) -> int:
        return r.get_obj_type(obj)
