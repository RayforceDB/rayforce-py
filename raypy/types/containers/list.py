from __future__ import annotations
import typing as t

from raypy import _rayforce_c as r
from raypy.core.ffi import FFI
from raypy.types.base import Container
from raypy.types.registry import TypeRegistry


class List(Container):
    """
    Heterogeneous list type.
    """

    type_code = r.TYPE_LIST
    ray_name = "List"

    def _create_from_value(self, value: t.Sequence[t.Any]) -> r.RayObject:
        from raypy.utils.conversion import python_to_ray

        list_ptr = FFI.init_list()

        for item in value:
            if isinstance(item, Container) or hasattr(item, "ptr"):
                item_ptr = item.ptr
            else:
                item_ptr = python_to_ray(item)

            FFI.push_obj(list_ptr, item_ptr)

        return list_ptr

    def to_python(self) -> list:
        result = []
        for item in self:
            result.append(item)
        return result

    def __len__(self) -> int:
        return FFI.get_obj_length(self.ptr)

    def __getitem__(self, idx: int) -> t.Any:
        if idx < 0:
            idx = len(self) + idx
        if idx < 0 or idx >= len(self):
            raise IndexError(f"List index out of range: {idx}")

        item_ptr = FFI.at_idx(self.ptr, idx)
        return TypeRegistry.from_ptr(item_ptr)

    def __iter__(self) -> t.Iterator[t.Any]:
        for i in range(len(self)):
            yield self[i]

    def append(self, value: t.Any) -> None:
        from raypy.utils.conversion import python_to_ray

        if isinstance(value, Container) or hasattr(value, "ptr"):
            item_ptr = value.ptr
        else:
            item_ptr = python_to_ray(value)

        FFI.push_obj(self.ptr, item_ptr)


TypeRegistry.register(r.TYPE_LIST, List)
