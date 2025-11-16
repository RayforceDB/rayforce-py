from __future__ import annotations

from typing import Any

from raypy import _rayforce as r
from raypy.core import FFI
from raypy.types import primitive as p
from raypy.types import container as c
from raypy.types import scalar as s


class Expression:
    """
    Essentially, a list which could be executed as a function with arguments.
    """

    ptr: r.RayObject

    def __init__(self, *args) -> None:
        self.ptr = FFI.init_list()

        for arg in args:
            FFI.push_obj(
                iterable=self.ptr, ptr=c.from_python_type_to_raw_rayobject(arg)
            )

    def __len__(self) -> int:
        return FFI.get_obj_length(self.ptr)

    def __getitem__(self, idx: int) -> Any:
        if idx < 0 or idx >= len(self):
            raise IndexError("Expression index out of range")

        return c.convert_raw_rayobject_to_raypy_type(FFI.at_idx(self.ptr, idx))

    def __iter__(self) -> Any:
        for i in range(len(self)):
            yield self.__getitem__(i)

    def __str__(self) -> str:
        return f"Expression[{', '.join([str(i) for i in self])}]"

    def __repr__(self) -> str:
        return self.__str__()


class SelectQuery:
    """
    Query to perform select operation.
    """

    ptr: r.RayObject

    def __validate(
        self,
        attributes: dict[str, str | Expression | dict[str, str]],
        select_from: str | SelectQuery | c.Table,
        where: Expression | None = None,
    ) -> None:
        self.attr_keys = attributes.keys()
        self.attr_values = attributes.values()

        if not select_from:
            raise ValueError("Attribute select_from is required.")

        if where is not None:
            if not isinstance(where, Expression):
                raise ValueError("Attribute where should be an Expression.")

        if any([not isinstance(key, str) for key in self.attr_keys]):
            raise ValueError("Query keys should be Python strings.")

        if any(
            [
                not isinstance(value, (str, Expression, dict))
                for value in self.attr_values
            ]
        ):
            raise ValueError(
                "Query values should be Python strings or Raypy expression."
            )

        self.attributes = attributes
        self.select_from = select_from
        self.where = where

    def __build_query(self) -> None:
        length = len(self.attr_keys) + 1 if not self.where else len(self.attr_keys) + 2
        self._query_keys = FFI.init_vector(type_code=s.Symbol.type_code, length=length)
        self._query_values = FFI.init_list()

        for idx, key in enumerate(self.attr_keys):
            # Fill query keys with requested attributes
            FFI.insert_obj(
                insert_to=self._query_keys,
                idx=idx,
                ptr=c.from_python_type_to_raw_rayobject(key),
            )
        else:
            # Push "from" keyword to query keys
            FFI.insert_obj(
                insert_to=self._query_keys,
                idx=len(self.attr_keys),
                ptr=c.from_python_type_to_raw_rayobject("from"),
            )

        for value in self.attr_values:
            # Fill query values with requested attributes
            FFI.push_obj(
                iterable=self._query_values,
                ptr=c.from_python_type_to_raw_rayobject(value),
            )
        else:
            # Push "from" value to query values
            if isinstance(self.select_from, SelectQuery):
                expr = Expression(p.Operation.SELECT, self.select_from.ptr)
                FFI.push_obj(iterable=self._query_values, ptr=expr.ptr)
            else:
                FFI.push_obj(
                    iterable=self._query_values,
                    ptr=c.from_python_type_to_raw_rayobject(self.select_from),
                )

        if self.where is not None:
            FFI.insert_obj(
                insert_to=self._query_keys,
                idx=len(self.attr_keys) + 1,
                ptr=c.from_python_type_to_raw_rayobject("where"),
            )
            FFI.push_obj(
                iterable=self._query_values,
                ptr=self.where.ptr,
            )

        self.ptr = FFI.init_dict(self._query_keys, self._query_values)

    def __init__(
        self,
        attributes: dict[str, str | Expression | dict[str, str]],
        select_from: str | "SelectQuery",
        where: Expression | None = None,
    ) -> None:
        self.__validate(attributes=attributes, select_from=select_from, where=where)
        self.__build_query()

    def __str__(self) -> str:
        return str(c.Dict(ptr=self.ptr))

    def __repr__(self) -> str:
        return self.__str__()


class UpdateQuery:
    """
    Query to perform update operation
    """

    ptr: r.RayObject

    def __validate(
        self,
        update_from: str | SelectQuery | Expression | c.Table,
        attributes: dict[str, str | Expression],
        where: Expression | None = None,
    ) -> None:
        self.attr_keys = attributes.keys()
        self.attr_values = attributes.values()

        if not update_from:
            raise ValueError("Attribute update_from is required.")

        if where is not None:
            if not isinstance(where, Expression):
                raise ValueError("Attribute where should be an Expression.")

        self.attributes = attributes
        self.update_from = update_from
        self.where = where

    def __build_query(self) -> r.RayObject:
        length = len(self.attr_keys) + 1 if not self.where else len(self.attr_keys) + 2
        self._query_keys = FFI.init_vector(type_code=s.Symbol.type_code, length=length)
        self._query_values = FFI.init_list()

        for idx, key in enumerate(self.attr_keys):
            # Fill query keys with requested attributes
            FFI.insert_obj(
                insert_to=self._query_keys,
                idx=idx,
                ptr=c.from_python_type_to_raw_rayobject(key),
            )
        else:
            # Push "from" keyword to query keys
            FFI.insert_obj(
                insert_to=self._query_keys,
                idx=len(self.attr_keys),
                ptr=c.from_python_type_to_raw_rayobject("from"),
            )

        for value in self.attr_values:
            # Fill query values with requested attributes
            FFI.push_obj(
                iterable=self._query_values,
                ptr=c.from_python_type_to_raw_rayobject(value),
            )
        else:
            # Push "from" value to query values
            if isinstance(self.update_from, str):
                # We need to assign update_from symbol the "quoted"
                # attribute, so inplace update can happen.
                key = FFI.init_symbol(self.update_from)
                FFI.set_obj_attrs(key, 8)
                FFI.push_obj(iterable=self._query_values, ptr=key)
            else:
                FFI.push_obj(
                    iterable=self._query_values,
                    ptr=c.from_python_type_to_raw_rayobject(self.update_from),
                )

        if self.where is not None:
            FFI.insert_obj(
                insert_to=self._query_keys,
                idx=len(self.attr_keys) + 1,
                ptr=c.from_python_type_to_raw_rayobject("where"),
            )
            FFI.push_obj(
                iterable=self._query_values,
                ptr=self.where.ptr,
            )

        self.ptr = FFI.init_dict(self._query_keys, self._query_values)

    def __init__(
        self,
        update_from: str | c.Table,
        attributes: dict[str, str | Expression],
        where: Expression | None = None,
    ) -> None:
        self.__validate(update_from=update_from, attributes=attributes, where=where)
        self.__build_query()

    def __str__(self) -> str:
        return str(c.Dict(ptr=self.ptr))

    def __repr__(self) -> str:
        return self.__str__()


class InsertQuery:
    """
    Query to perform insert operation
    """

    ptr: r.RayObject

    def __validate(
        self,
        insert_to: str | c.Table,
        insertable: dict[str, str | Expression] | list[dict[str, str | Expression]],
    ) -> None:
        if not insert_to:
            raise ValueError("Attribute insert_to is required.")

        if not insertable:
            raise ValueError("No attributes to insert.")

        self.insert_to = insert_to
        self.insertable = insertable

    def __build_query(self) -> None:
        self.insertable_ptr = FFI.init_list()
        for attribute in self.insertable:
            FFI.push_obj(
                iterable=self.insertable_ptr,
                ptr=c.from_python_type_to_raw_rayobject(attribute),
            )

        self.insert_to_ptr = c.from_python_type_to_raw_rayobject(self.insert_to)

    def __init__(
        self,
        insert_to: str | c.Table,
        insertable: dict[str, str | Expression] | list[dict[str, str | Expression]],
    ) -> None:
        self.__validate(insert_to=insert_to, insertable=insertable)
        self.__build_query()

    def __str__(self) -> str:
        insertable = c.convert_raw_rayobject_to_raypy_type(self.insertable_ptr)
        insert_to = c.convert_raw_rayobject_to_raypy_type(self.insert_to_ptr)
        return f"InsertQuery(to: \n {insert_to.__repr__()} \n) with entries: \n {insertable} \n"

    def __repr__(self) -> str:
        return self.__str__()


class UpsertQuery:
    """
    Query to perform upsert operation
    """

    ptr: r.RayObject

    def __validate(
        self,
        upsert_to: str | c.Table,
        match_by_first: int,
        upsertable: dict[str, str | Expression] | list[dict[str, str | Expression]],
    ) -> None:
        if not upsert_to:
            raise ValueError("Attribute upsert_to is required.")

        if not upsertable:
            raise ValueError("No attributes to upsert.")

        if match_by_first <= 0 or match_by_first > len(upsertable):
            raise ValueError("Match should be by length of upsertable or lower.")

        self.upsert_to = upsert_to
        self.upsertable = upsertable
        self.match_by_first = match_by_first

    def __build_query(self) -> None:
        # Match low-level is a number of ordered fields provided in upsertable.
        self.match_ptr = FFI.init_i64(self.match_by_first)

        i_keys = FFI.init_vector(type_code=-r.TYPE_SYMBOL, length=len(self.upsertable))
        for idx, key in enumerate(self.upsertable.keys()):  # type: ignore
            FFI.insert_obj(
                insert_to=i_keys,
                idx=idx,
                ptr=c.from_python_type_to_raw_rayobject(key),
            )

        i_values = FFI.init_list()
        for column_data in self.upsertable.values():  # type: ignore
            # Convert to appropriate Vector type (like Table.__init__ does)
            if not column_data:
                FFI.push_obj(iterable=i_values, ptr=FFI.init_list())
            elif all(isinstance(x, str) for x in column_data):
                # String column -> Vector of Symbols
                vec = c.Vector(type_code=s.Symbol.type_code, items=column_data)
                FFI.push_obj(iterable=i_values, ptr=vec.ptr)
            elif all(
                isinstance(x, (int, float)) and not isinstance(x, bool)
                for x in column_data
            ):
                # Numeric column -> detect if int or float
                if all(isinstance(x, int) for x in column_data):
                    vec = c.Vector(type_code=s.I64.type_code, items=column_data)
                else:
                    vec = c.Vector(type_code=s.F64.type_code, items=column_data)
                FFI.push_obj(iterable=i_values, ptr=vec.ptr)
            elif all(isinstance(x, bool) for x in column_data):
                # Boolean column
                vec = c.Vector(type_code=s.B8.type_code, items=column_data)
                FFI.push_obj(iterable=i_values, ptr=vec.ptr)
            else:
                # Mixed types - keep as List
                _l = FFI.init_list()
                for value in column_data:
                    FFI.push_obj(
                        iterable=_l, ptr=c.from_python_type_to_raw_rayobject(value)
                    )
                FFI.push_obj(iterable=i_values, ptr=_l)

        self.upsertable_ptr = FFI.init_dict(i_keys, i_values)

        if isinstance(self.upsert_to, c.Table):
            self.upsert_to_ptr = self.upsert_to.ptr
        else:
            key = FFI.init_symbol(self.upsert_to)
            FFI.set_obj_attrs(key, 8)
            self.upsert_to_ptr = key

    def __init__(
        self,
        upsert_to: str | c.Table,
        match_by_first: int,
        upsertable: dict[str, str | Expression] | list[dict[str, str | Expression]],
    ) -> None:
        self.__validate(
            upsert_to=upsert_to,
            match_by_first=match_by_first,
            upsertable=upsertable,
        )
        self.__build_query()

    def __str__(self) -> str:
        upsertable = c.convert_raw_rayobject_to_raypy_type(self.upsertable_ptr)
        upsert_to = c.convert_raw_rayobject_to_raypy_type(self.upsert_to_ptr)
        return f"UpsertQuery(to: \n {str(upsert_to)} \n) with entries: \n {str(upsertable)} \n"

    def __repr__(self) -> str:
        return self.__str__()
