from __future__ import annotations

import typing as t

from rayforce import _rayforce_c as r
from rayforce.ffi import FFI
from rayforce.types.base import (
    ElementAccessContainerMixin,
    MappableContainerMixin,
    SearchContainerMixin,
    SortContainerMixin,
)
from rayforce.types.registry import TypeRegistry
from rayforce.utils.conversion import python_to_ray, ray_to_python


class Dict(
    SortContainerMixin,
    ElementAccessContainerMixin,
    SearchContainerMixin,
    MappableContainerMixin,
):
    type_code = r.TYPE_DICT
    ray_name = "DICT"

    @classmethod
    def from_items(
        cls,
        keys: t.Any,
        values: t.Any,
    ) -> t.Self:
        keys_ptr = keys.ptr if hasattr(keys, "ptr") else keys
        values_ptr = values.ptr if hasattr(values, "ptr") else values
        return cls(ptr=FFI.init_dict(keys_ptr, values_ptr))

    def _create_from_value(self, value: dict[t.Any, t.Any]) -> r.RayObject:
        from rayforce.types import Symbol
        from rayforce.types.containers import List, Vector

        return FFI.init_dict(
            keys=Vector(items=list(value.keys()), ray_type=Symbol).ptr,
            values=List(list(value.values())).ptr,
        )

    def to_python(self) -> dict:
        return {
            k.to_python() if hasattr(k, "to_python") else k: v.to_python()
            if hasattr(v, "to_python")
            else v
            for k, v in zip(
                TypeRegistry.from_ptr(FFI.get_dict_keys(self.ptr)),  # type: ignore[arg-type]
                TypeRegistry.from_ptr(FFI.get_dict_values(self.ptr)),  # type: ignore[arg-type]
                strict=True,
            )
        }

    def __len__(self) -> int:
        return FFI.get_obj_length(FFI.get_dict_keys(self.ptr))

    def __setitem__(self, key: t.Any, value: t.Any) -> None:
        FFI.set_obj(
            obj=self.ptr,
            idx=python_to_ray(key),
            value=python_to_ray(value),
        )

    def __getitem__(self, key: t.Any) -> t.Any:
        return ray_to_python(FFI.dict_get(self.ptr, python_to_ray(key)))

    def __iter__(self) -> t.Iterator[t.Any]:
        return iter(ray_to_python(FFI.get_dict_keys(self.ptr)))

    def keys(self) -> t.Any:
        return ray_to_python(FFI.get_dict_keys(self.ptr))

    def values(self) -> t.Any:
        return ray_to_python(FFI.get_dict_values(self.ptr))

    def items(self) -> t.Any:
        return zip(self.keys(), self.values(), strict=True)


TypeRegistry.register(r.TYPE_DICT, Dict)
