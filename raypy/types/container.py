from typing import Any, Iterable
import uuid
import datetime as dt

from raypy import _rayforce as r

from . import scalar


class List:
    """
    Rayforce list type

    List is a container of items which can be of any Rayforce type
    """

    ptr: r.RayObject

    ray_type_code = r.TYPE_LIST

    ray_create_method = "create_list"
    ray_append_method = "list_append"
    ray_length_method = "list_length"
    ray_get_item_method = "list_get_item"
    ray_set_item_method = "list_set_item"
    ray_remove_item_method = "list_remove_item"

    def __init__(
        self,
        items: Iterable[Any] | None = None,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if ray_obj is not None:
            if (_type := ray_obj.get_type()) != self.ray_type_code:
                raise ValueError(
                    f"Expected RayForce object of type {self.ray_type_code}, got {_type}"
                )
            self.ptr = ray_obj
            return

        if not isinstance(items, Iterable):
            raise ValueError("Value should be iterable")

        self.ptr = getattr(r.RayObject, self.ray_create_method)()

        if items:
            for item in items:
                self.append(item)

    @staticmethod
    def __get_ptr_from_list_item(item: Any) -> r.RayObject:
        if getattr(item, "ptr", None) is not None:  # If item is one of Raypy types
            return item.ptr
        elif isinstance(item, r.RayObject):
            return item
        return from_pythonic_to_raypy_type(value=item).ptr

    def append(self, item: Any) -> None:
        """
        Item can be one of the following:
            - Pythonic type value
            - Raw RayObject pointer
            - One of Raypy types
        """
        ptr = self.__get_ptr_from_list_item(item)
        getattr(self.ptr, self.ray_append_method)(ptr)

    def __len__(self) -> int:
        return getattr(self.ptr, self.ray_length_method)()

    def get(self, index: int) -> Any:
        if index < 0 or index >= len(self):
            raise IndexError("List index out of range")
        return from_pointer_to_raypy_type(
            ptr=getattr(self.ptr, self.ray_get_item_method)(index)
        )

    def set(self, index: int, item: Any) -> None:
        """
        Item can be one of the following:
            - Pythonic type value
            - Raw RayObject pointer
            - One of Raypy types
        """
        if index < 0 or index >= len(self):
            raise IndexError("List index out of range")

        ptr = self.__get_ptr_from_list_item(item)
        getattr(self.ptr, self.ray_set_item_method)(index, ptr)

    def remove(self, index: int) -> None:
        if index < 0 or index >= len(self):
            raise IndexError("List index out of range")

        getattr(self.ptr, self.ray_remove_item_method)(index)

    def __getitem__(self, index: int) -> Any:
        return self.get(index)

    def __setitem__(self, index: int, item: Any) -> None:
        self.set(index, item)

    def __iter__(self) -> Any:
        for i in range(len(self)):
            yield self.get(i)

    def __str__(self) -> str:
        items = [self.get(i).__repr__() for i in range(len(self))]
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
        value: dict[scalar.Symbol, Any] | None = None,
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
            if not isinstance(item, scalar.Symbol):
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
                scalar.Symbol(ray_obj=ptr).ptr
                for ptr in getattr(self.ptr, self.ray_get_keys)()
            ]
        )

    # TODO: Add deserealisation
    def values(self) -> List:
        return List(items=getattr(self.ptr, self.ray_get_values)())

    def get(self, key: str) -> Any:
        return getattr(self.ptr, self.ray_get)(scalar.Symbol(value=key).ptr)

    def __len__(self) -> int:
        return getattr(self.ptr, self.ray_length)()


def from_pythonic_to_raypy_type(
    value: Any,
) -> (
    scalar.Symbol
    | List
    | Dict
    | scalar.i64
    | scalar.b8
    | scalar.Date
    | scalar.Time
    | scalar.Timestamp
    | scalar.GUID
):
    """
    Convert a python type to Rayforce type.
    Supported python types:
        - str -> Symbol
        - int -> i64 (Always use i64 when converting from Python)
        - bool -> b8
        - datetime.date -> Date
        - datetime.time -> Time
        - datetime.datetime -> Timestamp
        - uuid.UUID -> GUID
        - list -> List
        - dict -> Dict

    Note that this function is automatically decides which Rayforce type to convert to,
    but it's also possible to initialise Rayforce type directly from python function.

    Since there are certain Rayforce types which do not have similar Python alternative,
    The following types can only be created directly interfacing the type:
        - char.py::c8
        - unsigned.py::u8
    """
    if value is None:
        raise ValueError("Value can not be None")

    if isinstance(value, str):
        return scalar.Symbol(value)
    elif isinstance(value, int) and not isinstance(value, bool):
        return scalar.i64(value)
    elif isinstance(value, bool):
        return scalar.b8(value)
    elif isinstance(value, dt.date):
        return scalar.Date(value)
    elif isinstance(value, dt.time):
        return scalar.Time(value)
    elif isinstance(value, dt.datetime):
        return scalar.Timestamp(value)
    elif isinstance(value, uuid.UUID):
        return scalar.GUID(value)
    elif isinstance(value, list):
        ll = List()
        for item in value:
            ll.append(from_pythonic_to_raypy_type(item))
        return ll
    elif isinstance(value, dict):
        dict_keys = List()
        dict_values = List()
        for item in value.keys():
            if not isinstance(item, str):
                raise ValueError("Dict keys should be of type str")
            dict_keys.append(scalar.Symbol(item))
        for item in value.values():
            dict_values.append(from_pythonic_to_raypy_type(item))
        return Dict(value=zip(dict_keys, dict_values))

    raise ValueError("Value type is not supported")


def from_pointer_to_raypy_type(
    ptr: r.RayObject,
) -> (
    scalar.Symbol
    | List
    | Dict
    | scalar.i64
    | scalar.b8
    | scalar.Date
    | scalar.Time
    | scalar.Timestamp
    | scalar.GUID
):
    """
    Convert a raw Rayforce type (RayObject) to one of the raypy types.
    """
    if ptr is None:
        raise ValueError("Pointer can not be None")

    ptr_type = ptr.get_type()

    if ptr_type == -r.TYPE_I16:
        return scalar.i16(ray_obj=ptr)
    elif ptr_type == -r.TYPE_I32:
        return scalar.i32(ray_obj=ptr)
    elif ptr_type == -r.TYPE_I64:
        return scalar.i64(ray_obj=ptr)
    elif ptr_type == -r.TYPE_F64:
        return scalar.f64(ray_obj=ptr)
    elif ptr_type == -r.TYPE_B8:
        return scalar.b8(ray_obj=ptr)
    elif ptr_type == -r.TYPE_C8:
        return scalar.c8(ray_obj=ptr)
    elif ptr_type == r.TYPE_GUID:
        return scalar.GUID(ray_obj=ptr)
    elif ptr_type == -r.TYPE_SYMBOL:
        return scalar.Symbol(ray_obj=ptr)
    elif ptr_type == -r.TYPE_TIME:
        return scalar.Time(ray_obj=ptr)
    elif ptr_type == -r.TYPE_TIMESTAMP:
        return scalar.Timestamp(ray_obj=ptr)
    elif ptr_type == -r.TYPE_DATE:
        return scalar.Date(ray_obj=ptr)
    elif ptr_type == -r.TYPE_U8:
        return scalar.u8(ray_obj=ptr)
    elif ptr_type == r.TYPE_LIST:
        return List(ray_obj=ptr)
    elif ptr_type == r.TYPE_DICT:
        return Dict(ray_obj=ptr)

    raise ValueError(f"RayObject type of {ptr_type} is not supported")
