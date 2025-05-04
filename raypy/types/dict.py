from typing import Any

from raypy import _rayforce as r

from .symbol import Symbol
from .list import List


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
