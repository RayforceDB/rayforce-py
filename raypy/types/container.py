



from typing import Any, Iterable

from raypy import _rayforce as r

from .scalar.symbol import Symbol


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


class Dict:
    """
    Rayforce dictionary type
    """

    ptr: r.RayObject

    ray_type_code = r.TYPE_DICT
    ray_init_method = "create_dict"
    ray_get_keys = "dict_keys"
    ray_get_values = "dict_values"
    ray_get = "dict_get"
    ray_length = "dict_length"

    # TODO: Add support for regular python types
    # TODO: Add support for Strings (vectors of C8)
    def __init__(
        self,
        value: dict[Symbol, Any] | None = None,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if ray_obj is not None:
            if (_type := ray_obj.get_type()) != self.ray_type_code:
                raise ValueError(
                    f"Expected RayForce object of type {self.ray_type_code}, got {_type}"
                )
            self.ptr = ray_obj
            return

        if value is None:
            raise ValueError("At least one argument is required")

        dict_keys = List()
        for item in value.keys():
            if not isinstance(item, Symbol):
                raise ValueError(
                    "All keys should be either Symbols or Strings (vector of C8)"
                )
            dict_keys.append(item.ptr)

        dict_values = List()
        for item in value.values():
            dict_values.append(item.ptr)

        try:
            self.ptr = getattr(r.RayObject, self.ray_init_method)(
                dict_keys.ptr, dict_values.ptr
            )
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    def keys(self) -> List:
        return List(
            items=[
                Symbol(ray_obj=ptr).ptr
                for ptr in getattr(self.ptr, self.ray_get_keys)()
            ]
        )

    # TODO: Add deserealisation
    def values(self) -> List:
        return List(items=getattr(self.ptr, self.ray_get_values)())

    def get(self, key: str) -> Any:
        return getattr(self.ptr, self.ray_get)(Symbol(value=key).ptr)

    def __len__(self) -> int:
        return getattr(self.ptr, self.ray_length)()
