from __future__ import annotations
from typing import Any, Iterable
import uuid

from raypy import api
from raypy.types import primitive
from raypy.types import common
from raypy.types import scalar
from raypy import _rayforce as r


class GUID(common.RaypyContainer):
    """
    Rayforce GUID type (Globally unique identifier)
    """

    _type = r.TYPE_GUID

    def __init__(
        self,
        value: str | uuid.UUID | bytes | bytearray | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        super().__init__(value, ray_obj=ray_obj)

        if not getattr(self, "ptr", None):
            self.ptr = api.init_guid(value)

    @property
    def value(self) -> uuid.UUID:
        return api.read_guid(self.ptr)

    @property
    def hex(self) -> str:
        return self.value.hex

    @property
    def urn(self) -> str:
        return f"urn:uuid:{str(self.value)}"

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"GUID({self})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, GUID):
            return self.value == other.value
        if isinstance(other, uuid.UUID):
            return self.value == other
        if isinstance(other, str):
            try:
                return self.value == uuid.UUID(other)
            except ValueError:
                return False

        return False


class Vector:
    """
    Rayforce vector type - collection of elements of scalar type
    """

    ptr: r.RayObject
    _type: int

    def __init__(
        self,
        class_type: scalar.ScalarType,
        length: int = 0,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if not hasattr(class_type, "_type"):
            raise ValueError(
                "Class type has to be an Python object with _type attribute"
            )

        self._type = -class_type._type

        if ray_obj is not None:
            if (_type := ray_obj.get_obj_type()) != self._type:
                raise ValueError(
                    f"Expected Vector object of type {self._type}, got {_type}"
                )

            self.ptr = ray_obj
            return

        self.ptr = api.init_vector(type_code=-self._type, length=length)

    def __len__(self) -> int:
        return api.get_obj_length(self.ptr)

    def __getitem__(self, idx: int) -> scalar.ScalarType:
        if idx < 0:
            idx = len(self) + idx

        if not 0 <= idx < len(self):
            raise IndexError("Vector index out of range")

        return from_rf_to_raypy(api.get_object_at_idx(self.ptr, idx))

    def __setitem__(self, idx: int, value: Any) -> None:
        if idx < 0:
            idx = len(self) + idx

        if not 0 <= idx < len(self):
            raise IndexError("Vector index out of range")

        api.insert_obj(self.ptr, idx, api.from_python_to_rayforce_type(value))

    def to_list(self) -> list:
        return [self[i] for i in range(len(self))]

    def __iter__(self) -> Any:
        for i in range(len(self)):
            yield self.__getitem__(i)

    def __str__(self) -> str:
        return f"Vector[{self.ptr.get_obj_type()}] of len {len(self)}"

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

    _type = r.TYPE_LIST

    def __init__(
        self,
        items: Iterable[Any] | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if ray_obj is not None:
            if (_type := ray_obj.get_obj_type()) != self._type:
                raise ValueError(
                    f"Expected RayForce object of type {self._type}, got {_type}"
                )

            self.ptr = ray_obj
            return

        self.ptr = api.init_list()

        if items:
            if not isinstance(items, Iterable):
                raise ValueError("Value should be iterable")

            for item in items:
                self.append(item)

    def append(self, item: Any) -> None:
        api.push_obj_to_iterable(self.ptr, api.from_python_to_rayforce_type(item))

    def __len__(self) -> int:
        return api.get_obj_length(self.ptr)

    def remove(self, index: int) -> None:
        if index < 0 or index >= len(self):
            raise IndexError("List index out of range")

        api.remove_object_at_idx(self.ptr, index)

    def __getitem__(self, idx: int) -> Any:
        if idx < 0 or idx >= len(self):
            raise IndexError("List index out of range")

        return from_rf_to_raypy(api.get_object_at_idx(self.ptr, idx))

    def __setitem__(self, idx: int, value: Any) -> None:
        if idx < 0 or idx >= len(self):
            raise IndexError("List index out of range")

        api.insert_obj(self.ptr, idx, api.from_python_to_rayforce_type(value))

    def __iter__(self) -> Any:
        for i in range(len(self)):
            yield self.__getitem__(i)

    def __str__(self) -> str:
        items = [self.__getitem__(i).__repr__() for i in range(len(self))]
        return f"[{', '.join(items)}]"

    def __repr__(self) -> str:
        return f"List({str(self)})"

    def __add__(self, addable: list | List) -> List:
        return List(
            [api.from_python_to_rayforce_type(i) for i in self]
            + [api.from_python_to_rayforce_type(i) for i in addable]
        )

    def __radd__(self, addable: list | List) -> List:
        return self.__add__(addable)


class Dict:
    """
    Rayforce dictionary type
    """

    ptr: r.RayObject

    _type = r.TYPE_DICT

    def __init__(
        self,
        value: dict[str | scalar.Symbol, Any] | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if ray_obj is not None:
            if (_type := ray_obj.get_obj_type()) != self._type:
                raise ValueError(
                    f"Expected RayForce object of type {self._type}, got {_type}"
                )

            self.ptr = ray_obj
            return

        if value is None:
            raise ValueError("At least one argument is required")

        self.ptr = api.init_dict(value=value or {})

    def keys(self) -> List:
        return List(items=api.get_dict_keys(self.ptr))

    def values(self) -> List:
        return List(items=api.get_dict_values(self.ptr))

    def get(self, key: Any) -> Any:
        return from_rf_to_raypy(api.get_dict_value_by_key(self.ptr, key))

    def __len__(self) -> int:
        return len(self.keys())

    def __str__(self) -> str:
        result = []
        keys_list = self.keys()
        for key in keys_list:
            value = self.get(str(key))
            result.append(f"\t{repr(key)}: {repr(value)}")
        return "{\n" + ",\n".join(result) + "\n}"

    def __repr__(self) -> str:
        return f"Dict({self.__str__()})"


class Table:
    """
    Rayforce table type
    """

    ptr: r.RayObject

    _type = r.TYPE_TABLE

    def __init__(
        self,
        columns: list[str] | None = None,
        values: list | None = None,
        *,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if ray_obj is not None:
            if (_type := ray_obj.get_obj_type()) != self._type:
                raise ValueError(
                    f"Expected RayForce object of type {self._type}, got {_type}"
                )

            self.ptr = ray_obj
            return

        if (columns is None or values is None) or len(columns) == 0:
            raise ValueError("Provide columns and values for table initialisation")

        if not all([isinstance(i, str) for i in columns]):
            raise ValueError("Column elements must be Python strings")

        # Assert columns vector and values list are having same length
        if len(columns) != len(values):
            raise ValueError("Keys and values lists must have the same length")

        self.ptr = api.init_table(columns=columns, values=values)

    def columns(self) -> List | Vector:
        return from_rf_to_raypy(api.get_table_keys(self.ptr))

    def values(self) -> List:
        return from_rf_to_raypy(api.get_table_values(self.ptr))

    def __str__(self) -> str:
        columns = self.columns()
        values = self.values()

        rows = list(zip(*values))

        all_rows = [columns] + rows
        col_widths = [max(len(str(cell)) for cell in col) for col in zip(*all_rows)]

        # Box drawing chars
        tl, tr = "┌", "┐"
        bl, br = "└", "┘"
        h, v = "─", "│"
        hl, hr, hm = "├", "┤", "┼"
        ct = "┬"
        cb = "┴"

        # Helper: line builder
        def line(left, mid, right):
            return left + mid.join(h * (w + 2) for w in col_widths) + right

        # Top, header separator, bottom
        top = line(tl, ct, tr)
        header_sep = line(hl, hm, hr)
        bottom = line(bl, cb, br)

        def format_row(row):
            # pad cell content with 1 space on each side
            return (
                v
                + v.join(f" {str(cell).ljust(w)} " for cell, w in zip(row, col_widths))
                + v
            )

        lines = [top, format_row(columns), header_sep]
        for row in rows:
            lines.append(format_row(row))
        lines.append(bottom)

        return "\n".join(lines)

    def __repr__(self) -> str:
        return str(self)


class Expression:
    ptr: r.RayObject

    def __init__(self, *args) -> None:
        self.ptr = api.init_list()

        for arg in args:
            api.push_obj_to_iterable(
                iterable=self.ptr, obj=api.from_python_to_rayforce_type(arg)
            )

    def __len__(self) -> int:
        return api.get_obj_length(self.ptr)

    def __getitem__(self, idx: int) -> Any:
        if idx < 0 or idx >= len(self):
            raise IndexError("List index out of range")

        return from_rf_to_raypy(api.get_object_at_idx(self.ptr, idx))

    def __iter__(self) -> Any:
        for i in range(len(self)):
            yield self.__getitem__(i)

    def __str__(self) -> str:
        return f"Expression[{', '.join([str(i) for i in self])}]"

    def __repr__(self) -> str:
        return self.__str__()


class SelectQuery:
    ptr: r.RayObject

    def __init__(
        self,
        attributes: dict[str, str | Expression],
        select_from: str | SelectQuery,
        where: Expression | None = None,
    ) -> None:
        if not select_from:
            raise ValueError("Attribute select_from is required.")

        attr_keys = attributes.keys()
        attr_values = attributes.values()
        attr_key_length = len(attr_keys) + 1

        if where is not None:
            if not isinstance(where, Expression):
                raise ValueError("Attribute where should be an Expression.")

            attr_key_length += 1

        if any([not isinstance(key, str) for key in attr_keys]):
            raise ValueError("Query keys should be Python strings.")

        if any([not isinstance(value, (str, Expression)) for value in attr_values]):
            raise ValueError(
                "Query values should be Python strings or Raypy expression."
            )

        self.attributes = attributes
        self.select_from = select_from
        self.where = where

        query_keys = api.init_vector(type_code=-r.TYPE_SYMBOL, length=attr_key_length)
        query_values = api.init_list()

        for idx, key in enumerate(attr_keys):
            api.insert_obj(
                source_obj=query_keys,
                idx=idx,
                value=api.from_python_to_rayforce_type(key),
            )
        else:
            # Push select_from key
            api.insert_obj(
                source_obj=query_keys,
                idx=len(attr_keys),
                value=api.from_python_to_rayforce_type("from"),
            )

        for value in attr_values:
            api.push_obj_to_iterable(
                iterable=query_values,
                obj=api.from_python_to_rayforce_type(value),
            )
        else:
            # Push select_from value
            if isinstance(select_from, SelectQuery):
                api.push_obj_to_iterable(
                    iterable=query_values,
                    obj=Expression(
                        primitive.Operation.SELECT,
                        select_from.ptr,
                    ).ptr,
                )
            else:
                api.push_obj_to_iterable(
                    iterable=query_values,
                    obj=api.from_python_to_rayforce_type(select_from),
                )

        if where is not None:
            api.insert_obj(
                source_obj=query_keys,
                idx=len(attr_keys) + 1,
                value=api.from_python_to_rayforce_type("where"),
            )
            api.push_obj_to_iterable(
                iterable=query_values,
                obj=where.ptr,
            )

        self.ptr = api.init_dict_from_rf_objects(query_keys, query_values)


class Lambda:
    ptr: r.RayObject

    def __init__(
        self,
        arguments: list[str],
        expressions: Iterable[Expression],
    ) -> None:
        lambda_args = api.init_vector(type_code=-r.TYPE_SYMBOL, length=len(arguments))
        for idx, arg in enumerate(arguments):
            api.insert_obj(
                source_obj=lambda_args,
                idx=idx,
                value=api.from_python_to_rayforce_type(arg),
            )

        lambda_expression = api.init_list()
        api.push_obj_to_iterable(
            iterable=lambda_expression,
            obj=primitive.Operation.DO.primitive,
        )
        for expr in expressions:
            api.push_obj_to_iterable(
                iterable=lambda_expression,
                obj=expr.ptr,
            )

        self.ptr = api.init_lambda(lambda_args, lambda_expression)


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
    r.TYPE_C8: scalar.C8,
    -r.TYPE_SYMBOL: scalar.Symbol,
    r.TYPE_SYMBOL: scalar.Symbol,
    -r.TYPE_TIME: scalar.Time,
    r.TYPE_TIME: scalar.Time,
    -r.TYPE_TIMESTAMP: scalar.Timestamp,
    r.TYPE_TIMESTAMP: scalar.Timestamp,
    -r.TYPE_DATE: scalar.Date,
    r.TYPE_DATE: scalar.Date,
    -r.TYPE_U8: scalar.U8,
    r.TYPE_U8: scalar.U8,
    r.TYPE_LIST: List,
    r.TYPE_DICT: Dict,
    r.TYPE_GUID: GUID,
    r.TYPE_TABLE: Table,
}

type RaypyType = (
    scalar.I16
    | scalar.I32
    | scalar.I64
    | scalar.F64
    | scalar.B8
    | scalar.C8
    | scalar.Symbol
    | scalar.U8
    | scalar.Date
    | scalar.Time
    | scalar.Timestamp
    | GUID
    | Vector
    | Dict
    | Table
)


def from_rf_to_raypy(ptr: r.RayObject) -> RaypyType:
    """
    Convert a raw Rayforce type (RayObject) to one of the raypy types.
    """

    ptr_type = ptr.get_obj_type()

    if class_type := RAY_TYPE_TO_CLASS_MAPPING.get(ptr_type):
        if api.is_vector(ptr):
            return Vector(class_type, ray_obj=ptr)
        else:
            return class_type(ray_obj=ptr)

    if ptr_type in (r.TYPE_UNARY, r.TYPE_BINARY, r.TYPE_VARY):
        try:
            return primitive.Operation.from_ptr(ptr)
        except ValueError as e1:
            try:
                # Lambda
                ...
            except ValueError as e2:
                raise "Unknown Unary/Binary/Vary operation" from e1 and e2

    raise ValueError(f"RayObject type of {ptr_type} is not supported")
