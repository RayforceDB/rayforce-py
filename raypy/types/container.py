from __future__ import annotations

import datetime as dt
import typing as t
import uuid

from raypy import api
from raypy.types import scalar, primitive
from raypy import _rayforce as r


class __RaypyContainer:
    """
    This class is an abstract object for all container types.

    Should not be used directly.
    """

    ptr: r.RayObject

    type_code: int

    def __init__(
        self,
        value: t.Any | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        if value is None and ptr is None:
            raise ValueError(
                f"{self.__class__.__name__} class requires at least one initialization argument."
            )

        if self.type_code is None:
            raise AttributeError(f"{self.__class__.__name__} type code is not set")

        if ptr is not None:
            if not isinstance(ptr, r.RayObject):
                raise ValueError(f"{ptr} object is not RayObject")
            if (_type := ptr.get_obj_type()) != self.type_code:
                raise ValueError(
                    f"Expected RayObject of type {self.type_code} for {self.__class__}, got {_type}",
                )

            self.ptr = ptr

    @property
    def value(self) -> t.Any:
        raise NotImplementedError

    def __str__(self) -> str:
        return f"{self.__class__}({self.value})"

    def __repr__(self) -> str:
        return self.__str__()


class Vector:
    """
    Rayforce vector type - collection of elements of scalar type.

    Type code: sets during initialisation explicitly.
    """

    ptr: r.RayObject

    type_code: int

    def __init__(
        self,
        type_code: int | None = None,
        length: int = 0,
        items: list[t.Any] | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        if ptr is not None:
            if not api.is_vector(ptr):
                raise ValueError(f"Expected vector object, got {ptr.get_obj_type()}")

            self.ptr = ptr
            self.type_code = ptr.get_obj_type()
            return

        if type_code is None:
            raise ValueError("Vector type code can not be None")

        self.type_code = -type_code

        if items is not None:
            self.ptr = api.init_vector(type_code=self.type_code, length=len(items))
            for idx, item in enumerate(items):
                item_to_push = from_python_type_to_raw_rayobject(item)
                if item_to_push.get_obj_type() != -self.type_code:
                    raise ValueError(
                        f"All vector values should have {-self.type_code} type"
                    )

                api.insert_obj(insert_to=self.ptr, idx=idx, ptr=item_to_push)
        else:
            self.ptr = api.init_vector(type_code=self.type_code, length=length)

    @property
    def value(self) -> tuple[t.Any]:
        return tuple([i for i in self])

    def __len__(self) -> int:
        return api.get_obj_length(self.ptr)

    def __getitem__(self, idx: int) -> t.Any:
        if idx < 0:
            idx = len(self) + idx

        if not 0 <= idx < len(self):
            raise IndexError("Vector index out of range")

        item_raw = api.at_idx(self.ptr, idx)
        return convert_raw_rayobject_to_raypy_type(item_raw)

    def __setitem__(self, idx: int, value: t.Any) -> None:
        if idx < 0:
            idx = len(self) + idx

        if not 0 <= idx < len(self):
            raise IndexError("Vector index out of range")

        api.insert_obj(
            insert_to=self.ptr, idx=idx, ptr=from_python_type_to_raw_rayobject(value)
        )

    def __iter__(self) -> t.Any:
        for i in range(len(self)):
            yield self.__getitem__(i)

    def __str__(self) -> str:
        return f"Vector[{self.type_code}]({', '.join(str(i) for i in self)})"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, eq: t.Any) -> bool:
        if isinstance(eq, Vector):
            if eq.type_code != self.type_code:
                return False

            if len(eq) != len(self):
                return False

            for idx, value in enumerate(self):
                if eq[idx] != value:
                    return False
            return True
        return False


class String(Vector):
    """
    Rayforce String type (vector of C8)

    Type code: 12
    """

    ptr: r.RayObject

    type_code = r.TYPE_C8

    def __init__(
        self, value: str | None = None, *, ptr: r.RayObject | None = None
    ) -> None:
        if ptr and (_type := ptr.get_obj_type()) != self.type_code:
            raise ValueError(f"Expected String RayObject, got {_type}")

        if value is not None:
            super().__init__(
                type_code=-self.type_code,
                items=[api.init_c8(i) for i in value],
            )
        else:
            super().__init__(ptr=ptr)

    @property
    def value(self) -> str:  # type: ignore
        return "".join([i.value for i in super().value])

    def __str__(self) -> str:
        return f"String({self.value})"

    def __repr__(self) -> str:
        return self.__str__()


class List(__RaypyContainer):
    """
    Rayforce list type.

    List is a container of items which can be of any Rayforce type.

    Type code: 0
    """

    ptr: r.RayObject

    type_code = r.TYPE_LIST

    def __init__(
        self,
        items: t.Iterable[t.Any] | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        super().__init__(value=items, ptr=ptr)

        if not getattr(self, "ptr", None):
            self.ptr = api.init_list()

            for item in items:  # type: ignore
                self.append(item)

    @property
    def value(self) -> list[t.Any]:
        return [i for i in self]

    def append(self, item: t.Any) -> None:
        api.push_obj(iterable=self.ptr, ptr=from_python_type_to_raw_rayobject(item))

    def __len__(self) -> int:
        return api.get_obj_length(self.ptr)

    def __getitem__(self, idx: int) -> t.Any:
        if idx < 0:
            idx = len(self) + idx

        if not 0 <= idx < len(self):
            raise IndexError("Vector index out of range")

        item_raw = api.at_idx(self.ptr, idx)
        return convert_raw_rayobject_to_raypy_type(item_raw)

    def __setitem__(self, idx: int, value: t.Any) -> None:
        if idx < 0:
            idx = len(self) + idx

        if not 0 <= idx < len(self):
            raise IndexError("Vector index out of range")

        api.insert_obj(
            insert_to=self.ptr, idx=idx, ptr=from_python_type_to_raw_rayobject(value)
        )

    def __iter__(self) -> t.Any:
        for i in range(len(self)):
            yield self.__getitem__(i)

    def __eq__(self, eq: t.Any) -> bool:
        if isinstance(eq, List):
            if len(eq) != len(self):
                return False

            for idx, value in enumerate(self):
                if eq[idx] != value:
                    return False
            return True
        return False


class Dict(__RaypyContainer):
    """
    Rayforce dictionary type.

    Type code: 99
    """

    ptr: r.RayObject

    type_code = r.TYPE_DICT

    def __init__(
        self,
        value: dict[str | scalar.Symbol, t.Any] | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        super().__init__(value=value, ptr=ptr)

        if not getattr(self, "ptr", None):
            _keys = value.keys()  # type: ignore
            _values = value.values()  # type: ignore

            dict_keys = Vector(type_code=scalar.Symbol.type_code, length=len(_keys))
            for idx, key in enumerate(_keys):
                dict_keys[idx] = key

            dict_values = List(_values)

            self.ptr = api.init_dict(dict_keys.ptr, dict_values.ptr)

    def keys(self) -> Vector:
        keys = api.get_dict_keys(self.ptr)
        return Vector(ptr=keys)

    def values(self) -> t.Any:
        return convert_raw_rayobject_to_raypy_type(ptr=api.get_dict_values(self.ptr))

    def get(self, key: t.Any) -> t.Any:
        key_ptr = api.init_symbol(key)
        return convert_raw_rayobject_to_raypy_type(
            ptr=api.dict_get(dict=self.ptr, key=key_ptr)
        )

    def __len__(self) -> int:
        return len(self.keys())

    def __str__(self) -> str:
        result = []
        keys_vector = self.keys()
        for key in keys_vector:
            value = self.get(key.value)
            result.append(f"\t{repr(key)}: {repr(value)}")
        return "{\n" + ",\n".join(result) + "\n}"

    def __repr__(self) -> str:
        return f"Dict({self.__str__()})"

    def __eq__(self, eq: t.Any) -> bool:
        if isinstance(eq, Dict):
            if self.keys() != eq.keys():
                return False
            if self.values() != eq.values():
                return False
            return True
        return False


class Table:
    """
    Rayforce table type.

    Type code: 98
    """

    ptr: r.RayObject

    type_code = r.TYPE_TABLE

    def __init__(
        self,
        columns: list[str] | None = None,
        values: list | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        if ptr is not None:
            if (_type := ptr.get_obj_type()) != self.type_code:
                raise ValueError(
                    f"Expected RayForce object of type {self.type_code}, got {_type}"
                )

            self.ptr = ptr
            return

        if (columns is None or values is None) or len(columns) == 0:
            raise ValueError("Provide columns and values for table initialisation")

        if not all([isinstance(i, str) for i in columns]):
            raise ValueError("Column elements must be Python strings")

        # Assert columns vector and values list are having same length
        if len(columns) != len(values):
            raise ValueError("Keys and values lists must have the same length")

        table_columns = Vector(type_code=scalar.Symbol.type_code, length=len(columns))
        for idx, column in enumerate(columns):
            table_columns[idx] = column

        table_values = List(values)

        self.ptr = api.init_table(columns=table_columns.ptr, values=table_values.ptr)

    def columns(self) -> t.Any:
        return convert_raw_rayobject_to_raypy_type(api.get_table_keys(self.ptr))

    def values(self) -> t.Any:
        return convert_raw_rayobject_to_raypy_type(api.get_table_values(self.ptr))

    def __str__(self) -> str:
        return api.repr_table(self.ptr)

    def __repr__(self) -> str:
        return f"Table[{self.columns()}]"

    def __eq__(self, eq: t.Any) -> bool:
        if isinstance(eq, Table):
            return eq.columns() == self.columns() and eq.values() == self.values()
        return False


RAY_TYPE_TO_CLASS_MAPPING = {
    -r.TYPE_I16: scalar.I16,
    r.TYPE_I16: scalar.I16,
    -r.TYPE_I32: scalar.I32,
    r.TYPE_I32: scalar.I32,
    -r.TYPE_I64: scalar.I64,
    r.TYPE_I64: scalar.I64,
    -r.TYPE_F64: scalar.F64,
    r.TYPE_F64: scalar.F64,
    -r.TYPE_B8: scalar.B8,
    r.TYPE_B8: scalar.B8,
    -r.TYPE_C8: scalar.C8,
    r.TYPE_C8: String,
    -r.TYPE_SYMBOL: scalar.Symbol,
    r.TYPE_SYMBOL: scalar.Symbol,
    -r.TYPE_TIME: scalar.Time,
    r.TYPE_TIME: scalar.Time,
    -r.TYPE_TIMESTAMP: scalar.Timestamp,
    r.TYPE_TIMESTAMP: scalar.Timestamp,
    -r.TYPE_DATE: scalar.Date,
    r.TYPE_DATE: scalar.Date,
    -r.TYPE_U8: scalar.U8,
    -r.TYPE_GUID: scalar.GUID,
    r.TYPE_GUID: scalar.GUID,
    r.TYPE_U8: scalar.U8,
    r.TYPE_LIST: List,
    r.TYPE_DICT: Dict,
    r.TYPE_TABLE: Table,
}


def convert_raw_rayobject_to_raypy_type(ptr: r.RayObject) -> t.Any:
    ptr_type = ptr.get_obj_type()

    if ptr_type == 127:
        return api.get_error_message(ptr)

    if class_type := RAY_TYPE_TO_CLASS_MAPPING.get(ptr_type):
        if api.is_vector(ptr) and ptr_type != r.TYPE_C8:
            return Vector(type_code=ptr_type, ptr=ptr)
        return class_type(ptr=ptr)

    if ptr_type in (101, 102, 103):
        return primitive.Operation.from_ptr(ptr)

    if ptr_type == r.TYPE_NULL:
        return None

    raise ValueError(f"RayObject type of {ptr_type} is not supported")


def from_python_type_to_raw_rayobject(
    value: t.Any, is_ipc: bool = False
) -> r.RayObject:
    if isinstance(value, r.RayObject):
        return value
    elif hasattr(value, "ptr"):
        return value.ptr
    elif hasattr(value, "primitive"):
        return value.primitive
    elif isinstance(value, str):
        return scalar.Symbol(value).ptr
    elif isinstance(value, int) and not isinstance(value, bool):
        return scalar.I64(value).ptr
    elif isinstance(value, float):
        return scalar.F64(value).ptr
    elif isinstance(value, bool):
        return scalar.B8(value).ptr
    elif isinstance(value, dt.date):
        return scalar.Date(value).ptr
    elif isinstance(value, dt.time):
        return scalar.Time(value).ptr
    elif isinstance(value, dt.datetime):
        return scalar.Timestamp(value).ptr
    elif isinstance(value, uuid.UUID):
        return scalar.GUID(value).ptr
    elif isinstance(value, dict):
        return Dict(value).ptr
    elif isinstance(value, list):
        return List(value).ptr
    raise ValueError(
        f"Python type is not supported for Rayforce type conversion - {type(value)}"
    )
