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
        from rayforce.types.containers import Vector, List
        from rayforce.types import Symbol

        return FFI.init_dict(
            keys=Vector(items=value.keys(), type_code=Symbol.type_code).ptr,
            values=List([v for v in value.values()]).ptr,
        )

    def to_python(self) -> dict:
        return {
            k.to_python() if hasattr(k, "to_python") else k: v.to_python()
            if hasattr(v, "to_python")
            else v
            for k, v in zip(
                TypeRegistry.from_ptr(FFI.get_dict_keys(self.ptr)),
                TypeRegistry.from_ptr(FFI.get_dict_values(self.ptr)),
            )
        }

    def __len__(self) -> int:
        return FFI.get_obj_length(FFI.get_dict_keys(self.ptr))

    # TODO: Add __setitem__

    def __getitem__(self, key: t.Any) -> t.Any:
        from rayforce.utils.conversion import python_to_ray

        return ray_to_python(FFI.dict_get(self.ptr, python_to_ray(key)))

    def __iter__(self) -> t.Iterator[t.Any]:
        return iter(ray_to_python(FFI.get_dict_keys(self.ptr)))

    def keys(self) -> t.Any:
        return ray_to_python(FFI.get_dict_keys(self.ptr))

    def values(self) -> t.Any:
        return ray_to_python(FFI.get_dict_values(self.ptr))

    def items(self) -> t.Any:
        return zip(self.keys(), self.values())


TypeRegistry.register(r.TYPE_DICT, Dict)
