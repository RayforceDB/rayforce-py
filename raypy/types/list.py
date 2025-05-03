from typing import Any, Iterable

from raypy import _rayforce as r


class List:
    """
    Rayforce list type
    """

    # TODO: Add support for initialising the list with python values
    # TODO: Add serialisation when extracting values from list

    ptr: r.RayObject

    ray_type_code = r.TYPE_LIST

    ray_create_method = "create_list"
    ray_append_method = "list_append"
    ray_length_method = "list_length"
    ray_get_item_method = "list_get_item"
    ray_set_item_method = "list_set_item"
    ray_remove_item_method = "list_remove_item"

    def __init__(self, items: Iterable[r.RayObject] | None = None) -> None:
        self.ptr = getattr(r.RayObject, self.ray_create_method)()

        if items:
            for item in items:
                self.append(item)

    def append(self, item: r.RayObject) -> None:
        getattr(self.ptr, self.ray_append_method)(item)

    def __len__(self) -> int:
        return getattr(self.ptr, self.ray_length_method)()

    def get(self, index: int) -> r.RayObject:
        if index < 0 or index >= len(self):
            raise IndexError("List index out of range")

        return getattr(self.ptr, self.ray_get_item_method)(index)

    def set(self, index: int, item: r.RayObject) -> None:
        if index < 0 or index >= len(self):
            raise IndexError("List index out of range")

        getattr(self.ptr, self.ray_set_item_method)(index, item)

    def remove(self, index: int) -> None:
        if index < 0 or index >= len(self):
            raise IndexError("List index out of range")

        getattr(self.ptr, self.ray_remove_item_method)(index)

    def __getitem__(self, index: int) -> r.RayObject:
        return self.get(index)

    def __setitem__(self, index: int, item: r.RayObject):
        self.set(index, item)

    def __iter__(self) -> Any:
        for i in range(len(self)):
            yield self.get(i)

    def __str__(self) -> str:
        items = [str(self.get(i)) for i in range(len(self))]
        return f"[{', '.join(items)}]"

    def __repr__(self) -> str:
        return f"List({str(self)})"
