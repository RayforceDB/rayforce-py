from __future__ import annotations
import typing as t
from collections.abc import Iterable
from typing import Any, Callable
from rayforce.core import FFI
from rayforce import utils
from rayforce.types import (
    I64,
    Dict,
    List,
    QuotedSymbol,
    String,
    Symbol,
    Vector,
)
from rayforce.types.base import RayObject
from rayforce.types.operators import Operation
from rayforce import _rayforce_c as r
from rayforce.types.registry import TypeRegistry


class AggregationMixin:
    def count(self) -> Expression:
        return Expression(Operation.COUNT, self)

    def sum(self) -> Expression:
        return Expression(Operation.SUM, self)

    def mean(self) -> Expression:
        return Expression(Operation.AVG, self)

    def avg(self) -> Expression:
        return Expression(Operation.AVG, self)

    def first(self) -> Expression:
        return Expression(Operation.FIRST, self)

    def last(self) -> Expression:
        return Expression(Operation.LAST, self)

    def max(self) -> Expression:
        return Expression(Operation.MAX, self)

    def min(self) -> Expression:
        return Expression(Operation.MIN, self)

    def median(self) -> Expression:
        return Expression(Operation.MEDIAN, self)

    def distinct(self) -> Expression:
        return Expression(Operation.DISTINCT, self)

    def is_(self, other: bool) -> Expression:
        if not isinstance(other, bool):
            raise ValueError("is_ argument has to be bool")
        if other is True:
            return Expression(Operation.EVAL, self)
        return Expression(Operation.EVAL, Expression(Operation.NOT, self))

    def isin(self, values: list[Any]) -> Expression:
        if values and isinstance(values[0], str):
            vec = Vector(ray_type=Symbol, items=[QuotedSymbol(v) for v in values])
        else:
            vec = List(values)

        return Expression(Operation.IN, self, vec)


class OperatorMixin:
    def __and__(self, other) -> Expression:
        return Expression(Operation.AND, self, other)

    def __or__(self, other) -> Expression:
        return Expression(Operation.OR, self, other)

    def __add__(self, other) -> Expression:
        return Expression(Operation.ADD, self, other)

    def __sub__(self, other) -> Expression:
        return Expression(Operation.SUBTRACT, self, other)

    def __mul__(self, other) -> Expression:
        return Expression(Operation.MULTIPLY, self, other)

    def __truediv__(self, other) -> Expression:
        return Expression(Operation.DIVIDE, self, other)

    def __mod__(self, other) -> Expression:
        return Expression(Operation.MODULO, self, other)

    def __eq__(self, other) -> Expression:
        return Expression(Operation.EQUALS, self, other)

    def __ne__(self, other) -> Expression:
        return Expression(Operation.NOT_EQUALS, self, other)

    def __lt__(self, other) -> Expression:
        return Expression(Operation.LESS_THAN, self, other)

    def __le__(self, other) -> Expression:
        return Expression(Operation.LESS_EQUAL, self, other)

    def __gt__(self, other) -> Expression:
        return Expression(Operation.GREATER_THAN, self, other)

    def __ge__(self, other) -> Expression:
        return Expression(Operation.GREATER_EQUAL, self, other)

    def __radd__(self, other) -> Expression:
        return Expression(Operation.ADD, other, self)

    def __rsub__(self, other) -> Expression:
        return Expression(Operation.SUBTRACT, other, self)

    def __rmul__(self, other) -> Expression:
        return Expression(Operation.MULTIPLY, other, self)

    def __rtruediv__(self, other) -> Expression:
        return Expression(Operation.DIVIDE, other, self)


class Expression(AggregationMixin, OperatorMixin):
    def __init__(self, operation: Operation, *operands: t.Any) -> None:
        self.operation = operation
        self.operands = operands

    def compile(self) -> r.RayObject:
        if (
            self.operation == Operation.MAP
            and len(self.operands) == 2
            and isinstance(self.operands[0], Column)
            and isinstance(self.operands[1], Expression)
        ):
            return List(
                [
                    Operation.MAP,
                    Operation.AT,
                    self.operands[0].name,
                    List([Operation.WHERE, self.operands[1].compile()]),
                ]
            ).ptr

        # Standard expression compilation
        converted_operands = []
        for operand in self.operands:
            if isinstance(operand, Expression):
                converted_operands.append(operand.compile())
            elif isinstance(operand, Column):
                converted_operands.append(operand.name)
            elif hasattr(operand, "ptr"):
                converted_operands.append(operand)
            elif isinstance(operand, str):
                converted_operands.append(QuotedSymbol(operand))
            else:
                converted_operands.append(operand)
        return List([self.operation, *converted_operands]).ptr


class Column(AggregationMixin, OperatorMixin):
    def __init__(self, name: str, table: Table | None = None):
        self.name = name
        self.table = table

    def where(self, condition: Expression) -> Expression:
        return Expression(Operation.MAP, self, condition)


class TableInitMixin:
    def __init__(
        self,
        ptr: r.RayObject | str,
    ) -> None:
        self._ptr = ptr
        self.is_reference = isinstance(ptr, str)

    @classmethod
    def from_ptr(cls, ptr: r.RayObject) -> t.Self:
        if (_type := ptr.get_obj_type()) != cls.type_code:
            raise ValueError(
                f"Expected RayForce object of type {cls.type_code}, got {_type}"
            )
        return cls(ptr=ptr)

    @classmethod
    def from_name(cls, name: str) -> t.Self:
        return cls(ptr=name)

    @classmethod
    def from_csv(cls, column_types: list[RayObject], path: str) -> t.Self:
        return utils.eval_obj(
            List(
                [
                    Operation.READ_CSV,
                    Vector([c.ray_name for c in column_types], ray_type=Symbol),
                    String(path),
                ]
            )
        )

    @classmethod
    def from_dict(cls, items: dict[str, Vector]) -> t.Self:
        return cls.from_ptr(
            FFI.init_table(
                columns=Vector(items=items.keys(), ray_type=Symbol).ptr,
                values=List(items.values()).ptr,
            ),
        )


class TableValueAccessorMixin:
    _ptr: r.RayObject | str

    def columns(self) -> Any:
        return utils.ray_to_python(FFI.get_table_keys(self.evaled_ptr))

    def values(self) -> Any:
        return utils.ray_to_python(FFI.get_table_values(self.evaled_ptr))


class TableReprMixin:
    _ptr: r.RayObject | str

    def __str__(self) -> str:
        if isinstance(self._ptr, str):
            return Symbol(self._ptr)

        return FFI.repr_table(self._ptr)

    def __repr__(self) -> str:
        return f"Table[{self.columns()}]"


class TableQueryMixin:
    _ptr: r.RayObject | str

    def select(self, *cols, **computed_cols) -> SelectQueryBuilder:
        builder = SelectQueryBuilder(table=self.ptr)
        return builder.select(*cols, **computed_cols)

    def where(self, condition: Expression | Callable) -> SelectQueryBuilder:
        builder = SelectQueryBuilder(table=self.ptr)
        return builder.where(condition)

    def by(self, *cols, **computed_cols) -> SelectQueryBuilder:
        builder = SelectQueryBuilder(table=self.ptr)
        return builder.by(*cols, **computed_cols)

    def concat(self, *others: Table) -> Table:
        result = self.ptr
        for other in others:
            expr = Expression(Operation.CONCAT, result, other.ptr)
            result = utils.eval_obj(expr.compile())
        return self.from_ptr(result)

    def _join(self, other: Table, on: str | list[str], type_: Operation) -> Table:
        if type_ not in (Operation.INNER_JOIN, Operation.LEFT_JOIN):
            raise AssertionError("_join performed only on IJ or LJ")

        if isinstance(on, str):
            on = [on]

        return utils.eval_obj(
            List(
                [
                    type_,
                    Vector(items=on, ray_type=Symbol),
                    self.ptr,
                    other.ptr if isinstance(other, Table) else other,
                ]
            )
        )

    def _wj(
        self,
        type_: Operation,
        on: list[str],
        join_with: list[Table],
        interval: TableColumnInterval,
        **aggregations,
    ) -> Table:
        if type_ not in (Operation.WINDOW_JOIN, Operation.WINDOW_JOIN1):
            raise AssertionError("_wj performed only on WJ or WJ1")

        agg_dict = {}
        for name, expr in aggregations.items():
            if isinstance(expr, Expression):
                agg_dict[name] = expr.compile()
            elif isinstance(expr, Column):
                agg_dict[name] = expr.name
            else:
                agg_dict[name] = expr

        return utils.eval_obj(
            List(
                [
                    type_,
                    Vector(items=on, ray_type=Symbol),
                    interval.compile(),
                    self.ptr,
                    *[t.ptr for t in join_with],
                    agg_dict,
                ]
            )
        )

    def inner_join(self, other: Table, on: str | list[str]) -> Table:
        return self._join(other=other, on=on, type_=Operation.INNER_JOIN)

    def left_join(self, other: Table, on: str | list[str]) -> Table:
        return self._join(other=other, on=on, type_=Operation.LEFT_JOIN)

    def window_join(
        self,
        on: list[str],
        join_with: list[Any],
        interval: TableColumnInterval,
        **aggregations,
    ) -> Table:
        return self._wj(
            type_=Operation.WJ,
            on=on,
            join_with=join_with,
            interval=interval,
            **aggregations,
        )

    def window_join1(
        self,
        on: list[str],
        join_with: list[Any],
        interval: TableColumnInterval,
        **aggregations,
    ) -> Table:
        return self._wj(
            type_=Operation.WJ1,
            on=on,
            join_with=join_with,
            interval=interval,
            **aggregations,
        )

    def update(self, **kwargs) -> UpdateQuery:
        return UpdateQuery(self, **kwargs)

    def insert(self, *args, **kwargs) -> InsertQuery:
        return InsertQuery(self, *args, **kwargs)

    def upsert(self, *args, match_by_first: int, **kwargs) -> UpsertQuery:
        return UpsertQuery(self, *args, match_by_first=match_by_first, **kwargs)

    def save(self, name: str) -> None:
        FFI.binary_set(FFI.init_symbol(name), self.ptr)

    @property
    def ptr(self) -> r.RayObject:
        if isinstance(self._ptr, str):
            return QuotedSymbol(self._ptr).ptr
        return self._ptr

    @property
    def evaled_ptr(self) -> r.RayObject:
        if isinstance(self._ptr, str):
            return utils.eval_str(self._ptr).ptr
        else:
            return self._ptr


class Table(
    TableInitMixin,
    TableValueAccessorMixin,
    TableReprMixin,
    TableQueryMixin,
):
    type_code = r.TYPE_TABLE
    _ptr: r.RayObject | str
    is_reference: bool


# class _Table(TableValueAccessorMixin):
#     """
#     Rayforce table type.

#     Type code: 98
#     """

#     ptr: r.RayObject

#     type_code = r.TYPE_TABLE

#     def __init__(
#         self,
#         columns: list[str] | None = None,
#         values: list | None = None,
#         *,
#         ptr: r.RayObject | None = None,
#     ) -> None:
#         from rayforce.types.scalars import Symbol, I64, F64, B8
#         from rayforce.types.containers import Vector, List

#         if ptr is not None:
#             if (_type := ptr.get_obj_type()) != self.type_code:
#                 raise ValueError(
#                     f"Expected RayForce object of type {self.type_code}, got {_type}"
#                 )

#             self.ptr = ptr
#             return

#         if (columns is None or values is None) or len(columns) == 0:
#             raise ValueError("Provide columns and values for table initialisation")

#         if not all([isinstance(i, str) for i in columns]):
#             raise ValueError("Column elements must be Python strings")

#         # Assert columns vector and values list are having same length
#         if len(columns) != len(values):
#             raise ValueError("Keys and values lists must have the same length")

#         table_columns = Vector(ray_type=Symbol, length=len(columns))
#         for idx, column in enumerate(columns):
#             table_columns[idx] = column

#         # Convert each column to a Vector instead of keeping as List
#         table_values = List([])
#         for column_data in values:
#             # Auto-detect type and create appropriate Vector
#             if not column_data:
#                 # Empty column - use generic list
#                 table_values.append([])
#             elif all(isinstance(x, str) for x in column_data):
#                 # String column -> Vector of Symbols
#                 vec = Vector(ray_type=Symbol, items=column_data)
#                 table_values.append(vec)
#             elif all(
#                 isinstance(x, (int, float)) and not isinstance(x, bool)
#                 for x in column_data
#             ):
#                 # Numeric column -> detect if int or float
#                 if all(isinstance(x, int) for x in column_data):
#                     vec = Vector(ray_type=I64, items=column_data)
#                 else:
#                     vec = Vector(ray_type=F64, items=column_data)
#                 table_values.append(vec)
#             elif all(isinstance(x, bool) for x in column_data):
#                 # Boolean column
#                 vec = Vector(ray_type=B8, items=column_data)
#                 table_values.append(vec)
#             elif all(isinstance(x, datetime.time) for x in column_data) or all(
#                 isinstance(x, Time) for x in column_data
#             ):
#                 vec = Vector(ray_type=Time, items=column_data)
#                 table_values.append(vec)
#             elif all(isinstance(x, Timestamp) for x in column_data):
#                 vec = Vector(ray_type=Timestamp, items=column_data)
#                 table_values.append(vec)
#             else:
#                 # Mixed types or complex types - keep as List
#                 table_values.append(column_data)

#         self.ptr = FFI.init_table(columns=table_columns.ptr, values=table_values.ptr)

#     def columns(self) -> Any:
#         return utils.ray_to_python(FFI.get_table_keys(self.ptr))

#     def values(self) -> Any:
#         return utils.ray_to_python(FFI.get_table_values(self.ptr))

#     def __str__(self) -> str:
#         return FFI.repr_table(self.ptr)

#     def __repr__(self) -> str:
#         return f"Table[{self.columns()}]"

#     def __eq__(self, eq: Any) -> bool:
#         if isinstance(eq, _Table):
#             return eq.columns() == self.columns() and eq.values() == self.values()
#         return False


# class Table:
#     def __init__(
#         self,
#         name_or_data: str | None = None,
#         columns: list[str] | None = None,
#         values: list[Any] | None = None,
#         ptr=None,
#     ):
#         if isinstance(name_or_data, str):
#             self._table = name_or_data
#             self._is_ref = True
#         elif ptr is not None:
#             self._table = _Table(ptr=ptr)
#             self._is_ref = False
#         elif columns and values:
#             self._table = _Table(columns=columns, values=values)
#             self._is_ref = False
#         else:
#             raise ValueError("Must provide either name, columns/values, or ptr")

#     def __getattr__(self, name: str) -> Column:
#         if name.startswith("_"):
#             return object.__getattribute__(self, name)
#         return Column(name, table=self)

#     def select(self, *cols, **computed_cols) -> SelectQueryBuilder:
#         builder = SelectQueryBuilder(table=self._table)
#         return builder.select(*cols, **computed_cols)

#     def where(self, condition: Expression | Callable) -> SelectQueryBuilder:
#         builder = SelectQueryBuilder(table=self._table)
#         return builder.where(condition)

#     def by(self, *cols, **computed_cols) -> SelectQueryBuilder:
#         builder = SelectQueryBuilder(table=self._table)
#         return builder.by(*cols, **computed_cols)

#     def concat(self, *others: Table) -> Table:
#         result = self._table
#         for other in others:
#             other_table = other._table if isinstance(other, Table) else other
#             expr = Expression(Operation.CONCAT, result, other_table)
#             result = utils.eval_obj(expr.compile())
#         return Table(ptr=result._table.ptr)

#     @staticmethod
#     def concat_all(tables: list[Table]) -> Table:
#         if not tables:
#             raise ValueError("Must provide at least one table")
#         return tables[0].concat(*tables[1:])

#     def inner_join(self, other: Table, on: str | list[str]) -> Table:
#         from rayforce.types.containers import Vector, List
#         from rayforce.types.scalars import Symbol

#         if isinstance(on, str):
#             on = [on]

#         join_keys = Vector(ray_type=Symbol, items=on)
#         other_table = other._table if isinstance(other, Table) else other
#         self_table = self._table
#         result = utils.eval_obj(
#             List([Operation.IJ, join_keys, self_table, other_table])
#         )

#         return Table(ptr=result._table.ptr)

#     def left_join(self, other: Table, on: str | list[str]) -> Table:
#         from rayforce.types.containers import Vector, List
#         from rayforce.types.scalars import Symbol

#         if isinstance(on, str):
#             on = [on]

#         join_keys = Vector(ray_type=Symbol, items=on)
#         other_table = other._table if isinstance(other, Table) else other
#         self_table = self._table
#         result = utils.eval_obj(
#             List([Operation.LJ, join_keys, self_table, other_table])
#         )

#         return Table(ptr=result._table.ptr)

#     def window_join(
#         self,
#         on: list[str],
#         join_with: list[Any],
#         interval: TableColumnInterval,
#         **aggregations,
#     ) -> Table:
#         return self._wj(
#             method=Operation.WJ,
#             on=on,
#             join_with=join_with,
#             interval=interval,
#             **aggregations,
#         )

#     def window_join1(
#         self,
#         on: list[str],
#         join_with: list[Any],
#         interval: TableColumnInterval,
#         **aggregations,
#     ) -> Table:
#         return self._wj(
#             method=Operation.WJ1,
#             on=on,
#             join_with=join_with,
#             interval=interval,
#             **aggregations,
#         )

#     def _wj(
#         self,
#         method: Operation,
#         on: list[str],
#         join_with: list[Any],
#         interval: TableColumnInterval,
#         **aggregations,
#     ) -> Table:
#         from rayforce.types import Vector, Symbol

#         agg_dict = {}
#         for name, expr in aggregations.items():
#             if isinstance(expr, Expression):
#                 agg_dict[name] = expr.compile()
#             elif isinstance(expr, Column):
#                 agg_dict[name] = expr.name
#             else:
#                 agg_dict[name] = expr

#         join_keys = Vector(ray_type=Symbol, items=on)

#         result = utils.eval_obj(
#             List(
#                 [
#                     method,
#                     join_keys,
#                     interval.compile(),
#                     self._table,
#                     *[t.ptr for t in join_with],
#                     agg_dict,
#                 ]
#             )
#         )

#         return Table(ptr=result._table.ptr)

#     @property
#     def ptr(self) -> r.RayObject:
#         if isinstance(self._table, str):
#             self._table = utils.eval_str(self._table)

#         return self._table.ptr

#     def update(self, **kwargs) -> UpdateQuery:
#         return UpdateQuery(self._table, **kwargs)

#     def insert(self, *args, **kwargs) -> InsertQuery:
#         return InsertQuery(self._table, *args, **kwargs)

#     def upsert(
#         self,
#         *args,
#         match_by_first: int,
#         **kwargs,
#     ) -> UpsertQuery:
#         return UpsertQuery(self._table, *args, match_by_first=match_by_first, **kwargs)

#     def save(self, name: str) -> None:
#         FFI.binary_set(FFI.init_symbol(name), self._table.ptr)

#     def _get_table(self) -> _Table:
#         if self._is_ref:
#             return utils.eval_str(self._table)
#         return self._table

#     @property
#     def columns(self) -> list[str]:
#         if isinstance(self._table, _Table):
#             cols = self._table.columns()
#             return [col.value for col in cols]
#         return []

#     def values(self):
#         if self._is_ref:
#             table = utils.eval_str(self._table)
#             return table.values()
#         return self._table.values()

#     @property
#     def shape(self) -> tuple[int]:
#         if isinstance(self._table, _Table):
#             vals = self._table.values()
#             rows = len(vals[0]) if vals and len(vals) > 0 else 0
#             cols = len(self.columns)
#             return (rows, cols)
#         return (0, 0)

#     def __len__(self) -> int:
#         return self.shape[0]

#     def __getitem__(self, key):
#         if isinstance(key, str):
#             return self.__getattr__(key)
#         elif isinstance(key, list):
#             return self.select(*key).execute()
#         else:
#             raise NotImplementedError("Row/slice access not yet implemented")

#     @classmethod
#     def from_dict(cls, data: dict[str, list[Any]]) -> Table:
#         columns = list(data.keys())
#         values = list(data.values())
#         return cls(columns=columns, values=values)

#     @classmethod
#     def from_csv(
#         cls,
#         column_types: list[RayObject],
#         path: str,
#     ) -> Table:
#         query = List(
#             [
#                 Operation.READ_CSV,
#                 Vector([c.ray_name for c in column_types], ray_type=Symbol),
#                 String(path),
#             ]
#         )
#         return utils.eval_obj(query)

#     @classmethod
#     def get(cls, name: str) -> Table:
#         return cls(name)

#     @staticmethod
#     def _create_proxy(table: str | _Table) -> Table:
#         proxy = object.__new__(Table)
#         proxy._table = table
#         proxy._is_ref = isinstance(table, str)
#         return proxy

#     def __str__(self) -> str:
#         if isinstance(self._table, _Table):
#             return FFI.repr_table(self._table.ptr)
#         elif isinstance(self._table, str):
#             table = utils.eval_str(self._table)
#             return FFI.repr_table(table._table.ptr)
#         return f"Table('{self._table}')"

#     def __repr__(self) -> str:
#         if self._is_ref:
#             return f"Table('{self._table}')"
#         return f"Table(columns={self.columns})"

#     def xasc(self, *cols) -> Table:
#         from rayforce.types import List, Vector, Symbol

#         return utils.eval_obj(
#             List([Operation.XASC, self._table, Vector(cols, ray_type=Symbol)])
#         )

#     def xdesc(self, *cols) -> Table:
#         from rayforce.types import List, Vector, Symbol

#         return utils.eval_obj(
#             List(
#                 [
#                     Operation.XDESC,
#                     self._table,
#                     Vector(cols, ray_type=Symbol),
#                 ]
#             )
#         )


class SelectQuery:
    """
    Query to perform select operation.
    """

    ptr: r.RayObject

    def __validate(
        self,
        attributes: dict[str, str | Expression | dict[str, str]],
        select_from: str | SelectQuery | Table,
        where: Expression | None = None,
    ) -> None:
        self.attr_keys = attributes.keys()
        self.attr_values = attributes.values()

        if not select_from:
            raise ValueError("Attribute select_from is required.")

        if where is not None:
            if not isinstance(where, r.RayObject):
                raise ValueError("Attribute where should be an Expression.")

        if any([not isinstance(key, str) for key in self.attr_keys]):
            raise ValueError("Query keys should be Python strings.")

        self.attributes = attributes
        self.select_from = select_from
        self.where = where

    def __build_query(self) -> None:
        from rayforce.types.scalars import Symbol

        length = len(self.attr_keys) + 1 if not self.where else len(self.attr_keys) + 2
        self._query_keys = FFI.init_vector(type_code=Symbol.type_code, length=length)
        self._query_values = FFI.init_list()

        for idx, key in enumerate(self.attr_keys):
            # Fill query keys with requested attributes
            FFI.insert_obj(
                iterable=self._query_keys,
                idx=idx,
                ptr=utils.python_to_ray(key),
            )
        else:
            # Push "from" keyword to query keys
            FFI.insert_obj(
                iterable=self._query_keys,
                idx=len(self.attr_keys),
                ptr=utils.python_to_ray("from"),
            )

        for value in self.attr_values:
            # Fill query values with requested attributes
            FFI.push_obj(
                iterable=self._query_values,
                ptr=utils.python_to_ray(value),
            )
        else:
            # Push "from" value to query values
            if isinstance(self.select_from, SelectQuery):
                expr = Expression(Operation.SELECT, self.select_from.ptr)
                FFI.push_obj(iterable=self._query_values, ptr=expr.ptr)
            else:
                FFI.push_obj(
                    iterable=self._query_values,
                    ptr=utils.python_to_ray(self.select_from),
                )

        if self.where is not None:
            FFI.insert_obj(
                iterable=self._query_keys,
                idx=len(self.attr_keys) + 1,
                ptr=utils.python_to_ray("where"),
            )
            FFI.push_obj(
                iterable=self._query_values,
                ptr=self.where,
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
        from rayforce.types.containers import Dict

        return str(Dict(ptr=self.ptr))

    def __repr__(self) -> str:
        return self.__str__()


class SelectQueryBuilder:
    def __init__(
        self,
        table: str | Table,
        select_cols: tuple[Any] | None = None,
        where_conditions: list[Expression] | None = None,
        by_cols: dict[str, Expression | str] | None = None,
    ):
        self._table = table
        self._select_cols = select_cols
        self._where_conditions = where_conditions or []
        self._by_cols = by_cols or {}

    def select(self, *cols, **computed_cols) -> SelectQueryBuilder:
        return SelectQueryBuilder(
            table=self._table,
            select_cols=(cols, computed_cols),
            where_conditions=self._where_conditions,
            by_cols=self._by_cols,
        )

    def where(self, condition: Expression | Callable) -> SelectQueryBuilder:
        if callable(condition):
            temp_table = Table._create_proxy(self._table)
            condition = condition(temp_table)

        new_conditions = self._where_conditions.copy()
        new_conditions.append(condition)

        return SelectQueryBuilder(
            table=self._table,
            select_cols=self._select_cols,
            where_conditions=new_conditions,
            by_cols=self._by_cols,
        )

    def by(self, *cols, **computed_cols) -> SelectQueryBuilder:
        return SelectQueryBuilder(
            table=self._table,
            select_cols=self._select_cols,
            where_conditions=self._where_conditions,
            by_cols=(cols, computed_cols),
        )

    @property
    def ipc(self) -> r.RayObject:
        return (
            Expression(Operation.SELECT, self._build_legacy_query().ptr).compile().ptr
        )

    def execute(self) -> Table:
        query = self._build_legacy_query()
        return utils.ray_to_python(FFI.select(query=query.ptr))

    def _build_legacy_query(self) -> SelectQuery:
        attributes = {}

        if self._select_cols:
            cols, computed = self._select_cols

            for col in cols:
                if col == "*":
                    pass
                else:
                    attributes[col] = col

            for name, expr in computed.items():
                if isinstance(expr, Expression):
                    attributes[name] = expr.compile()
                elif isinstance(expr, Column):
                    attributes[name] = expr.name
                elif callable(expr):
                    temp_table = Table._create_proxy(self._table)
                    result = expr(temp_table)
                    attributes[name] = self._convert_expr(result)
                else:
                    attributes[name] = expr

        where_expr = None
        if self._where_conditions:
            combined = self._where_conditions[0]
            for cond in self._where_conditions[1:]:
                combined = combined & cond
            where_expr = combined.compile()

        if self._by_cols:
            by_attributes = {}
            cols, computed = self._by_cols

            for col in cols:
                by_attributes[col] = col

            for name, expr in computed.items():
                if isinstance(expr, Expression):
                    by_attributes[name] = expr.compile()
                elif isinstance(expr, Column):
                    by_attributes[name] = expr.name
                else:
                    by_attributes[name] = expr

            attributes["by"] = by_attributes

        return SelectQuery(
            select_from=self._table, attributes=attributes, where=where_expr
        )

    def _convert_expr(self, expr: Expression | Column) -> r.RayObject | str:
        if isinstance(expr, Expression):
            return expr.compile()
        elif isinstance(expr, Column):
            return expr.name
        return expr

    def __iter__(self):
        result = self.execute()
        return iter(result.values().value)

    def __repr__(self) -> str:
        parts = [f"SelectQueryBuilder(table={self._table}"]
        if self._select_cols:
            parts.append(", select=...")
        if self._where_conditions:
            parts.append(f", where={len(self._where_conditions)} conditions")
        return "".join(parts) + ")"


class UpdateQuery:
    def __init__(self, table: Table, **attributes):
        self.table = table
        self.attributes = attributes
        self.where_condition = None

    def where(self, condition: Expression) -> UpdateQuery:
        self.where_condition = condition
        return self

    def execute(self) -> Table:
        where_expr = None
        if self.where_condition:
            if isinstance(self.where_condition, Expression):
                where_expr = self.where_condition.compile()
            else:
                where_expr = self.where_condition

        converted_attrs = {}
        for key, value in self.attributes.items():
            if isinstance(value, Expression):
                converted_attrs[key] = value.compile()
            elif isinstance(value, Column):
                converted_attrs[key] = value.name
            elif isinstance(value, str):
                converted_attrs[key] = QuotedSymbol(value).ptr
            else:
                converted_attrs[key] = value

        query_items = dict(converted_attrs)
        if self.table.is_reference:
            cloned_table = FFI.quote(self.table.ptr)
            query_items["from"] = cloned_table
        else:
            query_items["from"] = self.table.ptr

        if where_expr is not None:
            query_items["where"] = where_expr

        new_table = FFI.update(query=Dict(query_items).ptr)
        if self.table.is_reference:
            return Table.from_name(Symbol(ptr=new_table).value)
        return Table.from_ptr(new_table)


class InsertQuery:
    def __init__(self, table: Table, *args, **kwargs):
        self.table = table
        self.args = args
        self.kwargs = kwargs

        if args and kwargs:
            raise ValueError("Insert query accepts args OR kwargs, not both")

        if args:
            first = args[0]

            if isinstance(first, Iterable) and not isinstance(first, (str, bytes)):
                _args = List([])
                for sub in args:
                    _args.append(
                        Vector(
                            items=sub,
                            ray_type=utils.python_to_ray(sub[0]).get_obj_type(),
                        )
                    )
                self.insertable_ptr = _args.ptr

            else:
                self.insertable_ptr = List(args).ptr

        elif kwargs:
            values = list(kwargs.values())
            first_val = values[0]

            if isinstance(first_val, Iterable) and not isinstance(
                first_val, (str, bytes)
            ):
                keys = Vector(items=list(kwargs.keys()), ray_type=Symbol)
                _values = List([])

                for val in values:
                    _values.append(
                        Vector(
                            items=val,
                            ray_type=utils.python_to_ray(val[0]).get_obj_type(),
                        )
                    )
                self.insertable_ptr = Dict.from_items(keys=keys, values=_values).ptr

            else:
                self.insertable_ptr = Dict(kwargs).ptr
        else:
            raise ValueError("No data to insert")

    def execute(self) -> Table:
        if self.table.is_reference:
            cloned_table = FFI.quote(self.table.ptr)
            new_table = FFI.insert(
                table=cloned_table,
                data=self.insertable_ptr,
            )
            return Table.from_name(Symbol(ptr=new_table).value)
        cloned_table = self.table.ptr
        new_table = FFI.insert(
            table=cloned_table,
            data=self.insertable_ptr,
        )
        return Table.from_ptr(new_table)


class UpsertQuery:
    def __init__(self, table: Table, *args, match_by_first: int, **kwargs) -> None:
        self.table = table
        self.args = args
        self.kwargs = kwargs

        if args and kwargs:
            raise ValueError("Upsert query accepts args OR kwargs, not both")

        if args:
            first = args[0]

            if isinstance(first, Iterable) and not isinstance(first, (str, bytes)):
                _args = List([])
                for sub in args:
                    _args.append(
                        Vector(
                            items=sub,
                            ray_type=utils.python_to_ray(sub[0]).get_obj_type(),
                        )
                    )
                self.upsertable_ptr = _args.ptr

            else:
                _args = List([])
                for sub in args:
                    _args.append(
                        Vector(
                            items=[sub],
                            ray_type=utils.python_to_ray(sub).get_obj_type(),
                        )
                    )
                self.upsertable_ptr = _args.ptr

        # TODO: for consistency with insert, allow to use single values isntead of vectors
        elif kwargs:
            values = list(kwargs.values())
            first_val = values[0]

            if isinstance(first_val, Iterable) and not isinstance(
                first_val, (str, bytes)
            ):
                keys = Vector(items=list(kwargs.keys()), ray_type=Symbol)
                _values = List([])

                for val in values:
                    _values.append(
                        Vector(
                            items=val,
                            ray_type=utils.python_to_ray(val[0]).get_obj_type(),
                        )
                    )
                self.upsertable_ptr = Dict.from_items(keys=keys, values=_values).ptr

            else:
                keys = Vector(items=list(kwargs.keys()), ray_type=Symbol)
                _values = List([])

                for val in values:
                    _values.append(
                        Vector(
                            items=[val],
                            ray_type=utils.python_to_ray(val).get_obj_type(),
                        )
                    )
                self.upsertable_ptr = Dict.from_items(keys=keys, values=_values).ptr
        else:
            raise ValueError("No data to insert")

        if match_by_first <= 0:
            raise ValueError("Match by first has to be greater than 0")

        self._match_by_first = I64(match_by_first)

    def execute(self) -> Table:
        if self.table.is_reference:
            cloned_table = FFI.quote(self.table.ptr)
            new_table = FFI.upsert(
                table=cloned_table,
                keys=self._match_by_first.ptr,
                data=self.upsertable_ptr,
            )
            return Table.from_name(Symbol(ptr=new_table).value)
        cloned_table = self.table.ptr
        new_table = FFI.upsert(
            table=cloned_table,
            keys=self._match_by_first.ptr,
            data=self.upsertable_ptr,
        )
        return Table.from_ptr(new_table)


class TableColumnInterval:
    def __init__(
        self,
        lower: int,
        upper: int,
        table: str | Table,
        column: str | Column,
    ) -> None:
        self.lower = lower
        self.upper = upper
        self.table = table
        self.column = column

    def compile(self) -> List:
        from rayforce.types import Vector, I64, QuotedSymbol

        return List(
            [
                Operation.MAP_LEFT,
                Operation.ADD,
                Vector([self.lower, self.upper], ray_type=I64),
                List(
                    [
                        Operation.AT,
                        self.table,
                        QuotedSymbol(
                            self.column.name
                            if isinstance(self.column, Column)
                            else self.column
                        ),
                    ]
                ),
            ]
        )


__all__ = [
    "Table",
    "Column",
    "Expression",
    "SelectQueryBuilder",
    "UpdateQuery",
    "InsertQuery",
    "UpsertQuery",
    "TableColumnInterval",
]

TypeRegistry.register(type_code=r.TYPE_TABLE, type_class=Table)
