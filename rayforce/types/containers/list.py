from __future__ import annotations

import typing as t

from rayforce import _rayforce_c as r
from rayforce.core.ffi import FFI
from rayforce.types.base import Container
from rayforce.types.registry import TypeRegistry
from rayforce.utils.conversion import python_to_ray


class List(Container):
    type_code = r.TYPE_LIST
    ray_name = "LIST"

    def _create_from_value(self, value: t.Sequence[t.Any]) -> r.RayObject:
        list_ptr = FFI.init_list()
        for item in value:
            FFI.push_obj(iterable=list_ptr, ptr=python_to_ray(item))

        return list_ptr

    def to_python(self) -> list:
        return list(self)

    def __len__(self) -> int:
        return FFI.get_obj_length(self.ptr)

    def __setitem__(self, idx: int, value: t.Any) -> None:
        FFI.insert_obj(
            iterable=self.ptr,
            ptr=python_to_ray(value),
            idx=idx,
        )

    def __getitem__(self, idx: int) -> t.Any:
        if idx < 0:
            idx = len(self) + idx
        if idx < 0 or idx >= len(self):
            raise IndexError(f"List index out of range: {idx}")

        return TypeRegistry.from_ptr(FFI.at_idx(self.ptr, idx))

    def __iter__(self) -> t.Iterator[t.Any]:
        for i in range(len(self)):
            yield self[i]

    def append(self, value: t.Any) -> None:
        FFI.push_obj(iterable=self.ptr, ptr=python_to_ray(value))


TypeRegistry.register(r.TYPE_LIST, List)
