from __future__ import annotations

from typing import Any

from raypy import _rayforce as r
from raypy import api
from raypy.types import primitive as p
from raypy.types import container as c


class Expression:
    """
    Essentially, a list which could be executed as a function with arguments.
    """

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
            raise IndexError("Expression index out of range")

        return c.from_rf_to_raypy(api.get_object_at_idx(self.ptr, idx))

    def __iter__(self) -> Any:
        for i in range(len(self)):
            yield self.__getitem__(i)

    def __str__(self) -> str:
        return f"Expression[{', '.join([str(i) for i in self])}]"

    def __repr__(self) -> str:
        return self.__str__()


class __Query:
    ptr: r.RayObject

    _query_keys: r.RayObject
    _query_values: r.RayObject

    def _add_query_key(self, idx: int, key: r.RayObject) -> None:
        api.insert_obj(source_obj=self._query_keys, idx=idx, value=key)

    def _add_query_value(self, value: r.RayObject) -> None:
        api.push_obj_to_iterable(iterable=self._query_values, obj=value)

    def _append_where_attribute(self) -> None:
        if self.where is None:
            return

        self._add_query_key(
            idx=self.key_length, key=api.from_python_to_rayforce_type("where")
        )
        self._add_query_value(value=self.where.ptr)

    def __str__(self) -> str:
        return c.Dict(ray_obj=self.ptr)

    def __repr__(self) -> str:
        return self.__str__()


class SelectQuery(__Query):
    """
    Query to perform select operation.
    """

    def __validate(
        self,
        attributes: dict[str, str | Expression],
        select_from: str | SelectQuery,
        where: Expression | None = None,
    ) -> None:
        self.attr_keys = attributes.keys()
        self.attr_values = attributes.values()
        self.key_length = len(self.attr_keys) + 1

        if not select_from:
            raise ValueError("Attribute select_from is required.")

        if where is not None:
            if not isinstance(where, Expression):
                raise ValueError("Attribute where should be an Expression.")

            self.key_length += 1

        if any([not isinstance(key, str) for key in self.attr_keys]):
            raise ValueError("Query keys should be Python strings.")

        if any(
            [not isinstance(value, (str, Expression)) for value in self.attr_values]
        ):
            raise ValueError(
                "Query values should be Python strings or Raypy expression."
            )

        self.attributes = attributes
        self.select_from = select_from
        self.where = where

    def __build_query(self) -> None:
        self._query_keys = api.init_vector(
            type_code=-r.TYPE_SYMBOL, length=self.key_length
        )
        self._query_values = api.init_list()

        for idx, key in enumerate(self.attr_keys):
            # Fill query keys with requested attributes
            self._add_query_key(idx=idx, key=api.from_python_to_rayforce_type(key))
        else:
            # Push "from" keyword to query keys
            key = api.from_python_to_rayforce_type("from")
            self._add_query_key(idx=len(self.attr_keys), key=key)

        for value in self.attr_values:
            # Fill query values with requested attributes
            self._add_query_value(value=api.from_python_to_rayforce_type(value))
        else:
            # Push "from" value to query values
            if isinstance(self.select_from, SelectQuery):
                self._add_query_value(
                    value=Expression(p.Operation.SELECT, self.select_from.ptr)
                )
            else:
                self._add_query_value(
                    value=api.from_python_to_rayforce_type(self.select_from)
                )

        self._append_where_attribute()
        self.ptr = api.init_dict_from_rf_objects(self._query_keys, self._query_values)

    def __init__(
        self,
        attributes: dict[str, str | Expression],
        select_from: str | "SelectQuery",
        where: Expression | None = None,
    ) -> None:
        self.__validate(attributes=attributes, select_from=select_from, where=where)
        self.__build_query()


class UpdateQuery(__Query):
    """
    Query to perform update operation
    """

    def __validate(
        self,
        update_from: str | SelectQuery | Expression | c.Table,
        attributes: dict[str, str | Expression],
        where: Expression = None,
    ) -> None:
        self.attr_keys = attributes.keys()
        self.attr_values = attributes.values()
        self.key_length = len(self.attr_keys) + 1

        if not update_from:
            raise ValueError("Attribute update_from is required.")

        if where is not None:
            if not isinstance(where, Expression):
                raise ValueError("Attribute where should be an Expression.")

            self.key_length += 1

        self.attributes = attributes
        self.update_from = update_from
        self.where = where

    def __build_query(self) -> r.RayObject:
        self._query_keys = api.init_vector(
            type_code=-r.TYPE_SYMBOL, length=self.key_length
        )
        self._query_values = api.init_list()

        for idx, key in enumerate(self.attr_keys):
            # Fill query keys with requested attributes
            self._add_query_key(idx=idx, key=api.from_python_to_rayforce_type(key))
        else:
            # Push "from" keyword to query keys
            key = api.from_python_to_rayforce_type("from")
            self._add_query_key(idx=len(self.attr_keys), key=key)

        for value in self.attr_values:
            # Fill query values with requested attributes
            self._add_query_value(value=api.from_python_to_rayforce_type(value))
        else:
            # Push "from" value to query values
            if isinstance(self.update_from, SelectQuery):
                self._add_query_value(
                    value=Expression(p.Operation.SELECT, self.update_from.ptr)
                )
            elif isinstance(self.update_from, str):
                # We need to assign update_from symbol the "quoted"
                # attribute, so inplace update can happen.
                key = api.init_symbol(self.update_from)
                api.set_obj_attributes(key, 8)
                self._add_query_value(value=key)
            else:
                self._add_query_value(
                    value=api.from_python_to_rayforce_type(self.update_from)
                )

        self._append_where_attribute()
        self.ptr = api.init_dict_from_rf_objects(self._query_keys, self._query_values)

    def __init__(
        self,
        update_from: str | SelectQuery | c.Table,
        attributes: dict[str, str | Expression],
        where: Expression = None,
    ) -> None:
        self.__validate(update_from=update_from, attributes=attributes, where=where)
        self.__build_query()


class InsertQuery(__Query):
    """
    Query to perform insert operation
    """

    def __validate(
        self,
        insert_to: str | c.Table,
        insertable: dict[str, str | Expression] | list[dict[str, str | Expression]],
    ) -> None:
        if not insert_to:
            raise ValueError("Attribute insert_to is required.")

        if not insertable:
            raise ValueError("No attributes to insert.")

        # If insert happens not inplace, validate columns width immediately.
        # But if it happens inplace, delegate to RF error raise if width is invalid.
        if isinstance(insert_to, c.Table):
            if not all(
                [len(attribute) == len(insert_to.columns) for attribute in insertable]
            ):
                raise ValueError(
                    "Attributes are having invalid length for table insert."
                )

        self.insert_to = insert_to
        self.insertable = insertable

    def __build_query(self) -> None:
        if isinstance(self.insertable, list):
            self.insertable_ptr = api.init_list()
            for attribute in self.insertable:
                api.push_obj_to_iterable(
                    iterable=self.insertable_ptr,
                    obj=api.from_python_to_rayforce_type(attribute),
                )
        else:
            self.insertable_ptr = api.from_python_to_rayforce_type(self.insertable)

        self.insert_to_ptr = api.from_python_to_rayforce_type(self.insert_to)

    def __init__(
        self,
        insert_to: str | c.Table,
        insertable: dict[str, str | Expression] | list[dict[str, str | Expression]],
    ) -> None:
        self.__validate(insert_to=insert_to, insertable=insertable)
        self.__build_query()


class UpsertQuery(__Query):
    """
    Query to perform upsert operation
    """

    def __validate(
        self,
        upsert_to: str | c.Table,
        match: str | list[str],
        upsertable: dict[str, str | Expression] | list[dict[str, str | Expression]],
    ) -> None:
        if not upsert_to:
            raise ValueError("Attribute upsert_to is required.")

        if not upsertable:
            raise ValueError("No attributes to upsert.")

        # If upsert happens not inplace, validate columns width immediately.
        # But if it happens inplace, delegate to RF error raise if width is invalid.
        if isinstance(upsert_to, c.Table):
            if isinstance(upsertable, list):
                if not all(
                    [len(attribute) == len(upsert_to.columns()) for attribute in upsertable]
                ):
                    raise ValueError(
                        "Attributes are having invalid length for table upsert."
                    )
            else:
                if len(upsertable) != len(upsert_to.columns()):
                    raise ValueError(
                        "Attributes are having invalid length for table upsert."
                    )

        if not match:
            raise ValueError("Attribute match is required.")

        if isinstance(match, list) and not all(
            [m and isinstance(m, str) for m in match]
        ):
            raise ValueError("Match attributes should be non-empty strings.")

        self.upsert_to = upsert_to
        self.upsertable = upsertable
        self.match = match

    def __build_query(self) -> None:
        # Match low-level is a number of ordered fields provided in upsertable.
        self.match_ptr = api.init_i64(len(self.match))

        if isinstance(self.upsertable, list):
            self.upsertable_ptr = api.init_list()
            for i in self.upsertable:
                i_keys = api.init_vector(type_code=-r.TYPE_SYMBOL, length=len(i))
                for idx, key in enumerate(i.keys()):
                    api.insert_obj(
                        source_obj=i_keys,
                        idx=idx,
                        value=api.from_python_to_rayforce_type(key),
                    )
                i_values = api.init_list()
                for value in i.values():
                    api.push_obj_to_iterable(
                        iterable=i_values,
                        obj=api.from_python_to_rayforce_type(value)
                    )
                api.push_obj_to_iterable(
                    iterable=self.upsertable_ptr,
                    obj=api.init_dict_from_rf_objects(i_keys, i_values),
                )
        else:
            i_keys = api.init_vector(type_code=-r.TYPE_SYMBOL, length=len(self.upsertable))
            for idx, key in enumerate(self.upsertable.keys()):
                api.insert_obj(
                    source_obj=i_keys,
                    idx=idx,
                    value=api.from_python_to_rayforce_type(key),
                )
            i_values = api.init_list()
            for value in self.upsertable.values():
                api.push_obj_to_iterable(
                    iterable=i_values,
                    obj=api.from_python_to_rayforce_type(value)
                )

            self.upsertable_ptr = api.init_dict_from_rf_objects(i_keys, i_values)

        if isinstance(self.upsert_to, c.Table):
            self.upsert_to_ptr = api.from_python_to_rayforce_type(self.upsert_to)
        else:
            key = api.init_symbol(self.upsert_to)
            api.set_obj_attributes(key, 8)
            self.upsert_to_ptr = api.from_python_to_rayforce_type(key)

    def __init__(
        self,
        upsert_to: str | c.Table,
        match: list[str],
        upsertable: dict[str, str | Expression] | list[dict[str, str | Expression]],
    ) -> None:
        self.__validate(upsert_to=upsert_to, match=match, upsertable=upsertable)
        self.__build_query()
