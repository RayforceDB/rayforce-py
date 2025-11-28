from __future__ import annotations
import typing as t

from rayforce import _rayforce_c as r
from rayforce.core.ffi import FFI
from rayforce.types.base import Container
from rayforce.types.registry import TypeRegistry
from rayforce.types import exceptions
from rayforce.utils.conversion import ray_to_python


class Dict(Container):
    type_code = r.TYPE_DICT
    ray_name = "Dict"

    def __init__(
        self,
        value: dict = None,
        *,
        ptr: r.RayObject | None = None,
        keys: t.Any = None,
        values: t.Any = None,
    ):
        if ptr is not None:
            self.ptr = ptr
            self._validate_ptr(ptr)
        elif value is not None:
            self.ptr = self._create_from_value(value)
        elif keys is not None and values is not None:
            keys_ptr = keys.ptr if hasattr(keys, "ptr") else keys
            values_ptr = values.ptr if hasattr(values, "ptr") else values
            self.ptr = FFI.init_dict(keys_ptr, values_ptr)
        else:
            raise exceptions.RayInitException(
                "Dict requires either value, ptr, or (keys + values)"
            )

    def _create_from_value(self, value: dict) -> r.RayObject:
        from rayforce.utils.conversion import python_to_ray
        from rayforce.types.containers import Vector
        from rayforce.types import Symbol

        # Convert keys and values to Lists
        keys = Vector(items=value.keys(), type_code=Symbol.type_code).ptr
        values_list = FFI.init_list()

        for v in value.values():
            FFI.push_obj(values_list, python_to_ray(v))

        return FFI.init_dict(keys, values_list)

    def to_python(self) -> dict:
        keys_ptr = FFI.get_dict_keys(self.ptr)
        values_ptr = FFI.get_dict_values(self.ptr)

        keys_obj = TypeRegistry.from_ptr(keys_ptr)
        values_obj = TypeRegistry.from_ptr(values_ptr)
        result = {}
        for k, v in zip(keys_obj, values_obj):
            py_key = k.to_python() if hasattr(k, "to_python") else k
            py_val = v.to_python() if hasattr(v, "to_python") else v
            result[py_key] = py_val

        return result

    def __len__(self) -> int:
        keys_ptr = FFI.get_dict_keys(self.ptr)
        return FFI.get_obj_length(keys_ptr)

    def __getitem__(self, key: t.Any) -> t.Any:
        from rayforce.utils.conversion import python_to_ray

        key_ptr = python_to_ray(key)
        value_ptr = FFI.dict_get(self.ptr, key_ptr)
        return ray_to_python(value_ptr)

    def __iter__(self) -> t.Iterator[t.Any]:
        keys_ptr = FFI.get_dict_keys(self.ptr)
        return iter(ray_to_python(keys_ptr))

    def keys(self) -> t.Any:
        keys_ptr = FFI.get_dict_keys(self.ptr)
        return ray_to_python(keys_ptr)

    def values(self) -> t.Any:
        values_ptr = FFI.get_dict_values(self.ptr)
        return ray_to_python(values_ptr)

    def items(self) -> t.Any:
        return zip(self.keys(), self.values())


TypeRegistry.register(r.TYPE_DICT, Dict)
