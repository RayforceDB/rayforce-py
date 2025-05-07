from typing import Any, Iterable, TypeVar, Generic, List as PyList
import uuid
import datetime as dt

from raypy import _rayforce as r

from . import scalar


T = TypeVar("T")


class Vector(Generic[T]):
    """
    Rayforce vector type - collection of elements of type T
    """

    ptr: r.RayObject
    class_type: scalar.ScalarType
    length: int
    ray_get_item_at_idx_method = "at_idx"
    ray_set_item_at_idx_method = "set_idx"

    def __init__(
        self,
        class_type: scalar.ScalarType,
        length: int = 0,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if not hasattr(class_type, "ray_type_code"):
            raise ValueError(
                "Class type has to be an object with ray_type_code attribute"
            )

        self.class_type = class_type
        self.length = length

        if ray_obj is not None:
            if (_type := ray_obj.get_type()) != class_type.ray_type_code:
                raise ValueError(
                    f"Expected Vector object of type {class_type.ray_type_code}, got {_type}"
                )
            self.ptr = ray_obj
            return

        try:
            self.ptr = r.RayObject.vector(class_type.ray_type_code, length)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during vector initialization - {str(e)}")

    def __len__(self) -> int:
        return self.length

    def __getitem__(self, idx: int) -> scalar.ScalarType:
        if idx < 0:
            idx = len(self) + idx

        if not 0 <= idx < len(self):
            raise IndexError("Vector index out of range")

        item = getattr(self.ptr, self.ray_get_item_at_idx_method)(idx)
        return from_pointer_to_raypy_type(item)

    def __setitem__(self, idx: int, value: scalar.ScalarType) -> None:
        if idx < 0:
            idx = len(self) + idx

        if not 0 <= idx < len(self):
            raise IndexError("Vector index out of range")

        if not hasattr(value, "ray_type_code"):
            raise ValueError(f"Expected Ray type object, got {type(value)}")

        getattr(self.ptr, self.ray_set_item_at_idx_method)(idx, value.ptr)

    def to_list(self) -> PyList[T]:
        return [self[i] for i in range(len(self))]

    def __str__(self) -> str:
        return f"Vector[{self.class_type}]({self.to_list()})"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Vector):
            return False
        if len(self) != len(other):
            return False
        try:
            return all(self[i] == other[i] for i in range(len(self)))
        except Exception:
            return False


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
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if ray_obj is not None:
            if (_type := ray_obj.get_type()) != self.ray_type_code:
                raise ValueError(
                    f"Expected RayForce object of type {self.ray_type_code}, got {_type}"
                )
            self.ptr = ray_obj
            return

        self.ptr = getattr(r.RayObject, self.ray_create_method)()

        if items:
            if not isinstance(items, Iterable):
                raise ValueError("Value should be iterable")
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

    def __init__(
        self,
        value: dict[str | scalar.Symbol, Any] | None = None,
        *,
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
            if not isinstance(item, (str, scalar.Symbol)):
                raise ValueError("All keys should be either str or Symbols")
            dict_keys.append(item)

        dict_values = List()
        for item in value.values():
            dict_values.append(item)

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

    def values(self) -> List:
        return List(items=getattr(self.ptr, self.ray_get_values)())

    def get(self, key: str) -> Any:
        return from_pointer_to_raypy_type(
            getattr(self.ptr, self.ray_get)(scalar.Symbol(value=key).ptr)
        )

    def __len__(self) -> int:
        return getattr(self.ptr, self.ray_length)()

    def __str__(self) -> str:
        result = []
        keys_list = self.keys()
        for i in keys_list:
            value = self.get(str(i))
            result.append(f"{repr(i)}: {repr(value)}")
        return "{" + ", ".join(result) + "}"

    def __repr__(self) -> str:
        return f"Dict({str(self)})"


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
        return Dict(value)

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
    | Vector
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
    elif ptr_type > 0:  # Positive type values generally indicate vector types
        return Vector(ptr_type, ray_obj=ptr)

    raise ValueError(f"RayObject type of {ptr_type} is not supported")
