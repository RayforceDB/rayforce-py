from __future__ import annotations
import datetime
from typing import Any, Callable
from raypy.core import FFI
from raypy import utils
from raypy.types import List, String, Symbol, Time, Timestamp, Vector
from raypy.types.base import RayObject
from raypy.types.operators import Operation
from raypy import _rayforce_c as r
from raypy.types.registry import TypeRegistry


class _Expression:
    """
    Essentially, a list which could be executed as a function with arguments.
    """

    ptr: r.RayObject

    def __init__(self, *args) -> None:
        self.ptr = FFI.init_list()

        for arg in args:
            FFI.push_obj(iterable=self.ptr, ptr=utils.python_to_ray(arg))

    def __len__(self) -> int:
        return FFI.get_obj_length(self.ptr)

    def __getitem__(self, idx: int) -> Any:
        if idx < 0 or idx >= len(self):
            raise IndexError("Expression index out of range")

        return utils.python_to_ray(FFI.at_idx(self.ptr, idx))

    def __iter__(self) -> Any:
        for i in range(len(self)):
            yield self.__getitem__(i)

    def __str__(self) -> str:
        return f"Expression[{', '.join([str(i) for i in self])}]"

    def __repr__(self) -> str:
        return self.__str__()


class Expression:
    def __init__(self, operation: Operation, *operands):
        self.operation = operation
        self.operands = operands

    def to_low_level(self) -> _Expression:
        from raypy.types.scalars import QuotedSymbol

        converted_operands = []

        for idx, operand in enumerate(self.operands):
            if isinstance(operand, Expression):
                converted_operands.append(operand.to_low_level())
            elif isinstance(operand, Column):
                converted_operands.append(operand.name)
            elif isinstance(operand, FilteredColumn):
                converted_operands.append(self._build_filtered_column(operand))
            elif hasattr(operand, "ptr"):
                converted_operands.append(operand)
            elif isinstance(operand, str):
                if self.operation == Operation.AT and idx == 1:
                    converted_operands.append(operand)
                else:
                    converted_operands.append(QuotedSymbol(operand))
            else:
                converted_operands.append(operand)

        return _Expression(self.operation.primitive, *converted_operands)

    def _build_filtered_column(self, filtered_col: FilteredColumn) -> _Expression:
        if isinstance(filtered_col.condition, Expression):
            where_expr = filtered_col.condition.to_low_level()
        elif isinstance(filtered_col.condition, Column):
            where_expr = filtered_col.condition.name
        else:
            where_expr = filtered_col.condition

        where_wrapped = _Expression(Operation.WHERE, where_expr)

        return _Expression(
            Operation.MAP, Operation.AT, filtered_col.column.name, where_wrapped
        )

    def count(self) -> Expression:
        return Expression(Operation.COUNT, self)

    def sum(self) -> Expression:
        return Expression(Operation.SUM, self)

    def mean(self) -> Expression:
        return Expression(Operation.AVG, self)

    def avg(self) -> Expression:
        return Expression(Operation.AVG, self)

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

    def __repr__(self) -> str:
        return f"Expression({self.operation.value}, {len(self.operands)} operands)"


class Column:
    def __init__(self, name: str, table: Table | None = None):
        self.name = name
        self.table = table

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

    def __radd__(self, other) -> Expression:
        return Expression(Operation.ADD, other, self)

    def __rsub__(self, other) -> Expression:
        return Expression(Operation.SUBTRACT, other, self)

    def __rmul__(self, other) -> Expression:
        return Expression(Operation.MULTIPLY, other, self)

    def __rtruediv__(self, other) -> Expression:
        return Expression(Operation.DIVIDE, other, self)

    def __and__(self, other) -> Expression:
        return Expression(Operation.AND, self, other)

    def __or__(self, other) -> Expression:
        return Expression(Operation.OR, self, other)

    def sum(self) -> Expression:
        return Expression(Operation.SUM, self)

    def mean(self) -> Expression:
        return Expression(Operation.AVG, self)

    def avg(self) -> Expression:
        return Expression(Operation.AVG, self)

    def max(self) -> Expression:
        return Expression(Operation.MAX, self)

    def min(self) -> Expression:
        return Expression(Operation.MIN, self)

    def count(self) -> Expression:
        return Expression(Operation.COUNT, self)

    def first(self) -> Expression:
        return Expression(Operation.FIRST, self)

    def last(self) -> Expression:
        return Expression(Operation.LAST, self)

    def median(self) -> Expression:
        return Expression(Operation.MEDIAN, self)

    def distinct(self) -> Expression:
        return Expression(Operation.DISTINCT, self)

    def isin(self, values: list[Any]) -> Expression:
        from raypy.types.scalars import QuotedSymbol, Symbol
        from raypy.types.containers import List, Vector

        if values and isinstance(values[0], str):
            quoted_items = [QuotedSymbol(v) for v in values]
            vec = Vector(type_code=Symbol.type_code, items=quoted_items)
        else:
            vec = List(values)

        return Expression(Operation.IN, self, vec)

    def where(self, condition: Expression) -> FilteredColumn:
        return FilteredColumn(self, condition)

    def __getitem__(self, condition: Expression) -> FilteredColumn:
        return self.where(condition)

    def __repr__(self) -> str:
        return f"Column('{self.name}')"


class FilteredColumn:
    def __init__(self, column: Column, condition: Expression):
        self.column = column
        self.condition = condition

    def sum(self) -> Expression:
        return Expression(Operation.SUM, self)

    def mean(self) -> Expression:
        return Expression(Operation.AVG, self)

    def avg(self) -> Expression:
        return Expression(Operation.AVG, self)

    def max(self) -> Expression:
        return Expression(Operation.MAX, self)

    def min(self) -> Expression:
        return Expression(Operation.MIN, self)

    def count(self) -> Expression:
        return Expression(Operation.COUNT, self)

    def __repr__(self) -> str:
        return f"FilteredColumn({self.column.name} where ...)"


class _Table:
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
        from raypy.types.scalars import Symbol, I64, F64, B8
        from raypy.types.containers import Vector, List

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

        table_columns = Vector(type_code=Symbol.type_code, length=len(columns))
        for idx, column in enumerate(columns):
            table_columns[idx] = column

        # Convert each column to a Vector instead of keeping as List
        table_values = List([])
        for column_data in values:
            # Auto-detect type and create appropriate Vector
            if not column_data:
                # Empty column - use generic list
                table_values.append([])
            elif all(isinstance(x, str) for x in column_data):
                # String column -> Vector of Symbols
                vec = Vector(type_code=Symbol.type_code, items=column_data)
                table_values.append(vec)
            elif all(
                isinstance(x, (int, float)) and not isinstance(x, bool)
                for x in column_data
            ):
                # Numeric column -> detect if int or float
                if all(isinstance(x, int) for x in column_data):
                    vec = Vector(type_code=I64.type_code, items=column_data)
                else:
                    vec = Vector(type_code=F64.type_code, items=column_data)
                table_values.append(vec)
            elif all(isinstance(x, bool) for x in column_data):
                # Boolean column
                vec = Vector(type_code=B8.type_code, items=column_data)
                table_values.append(vec)
            elif all(isinstance(x, datetime.time) for x in column_data) or all(
                isinstance(x, Time) for x in column_data
            ):
                vec = Vector(type_code=Time.type_code, items=column_data)
                table_values.append(vec)
            elif all(isinstance(x, Timestamp) for x in column_data):
                vec = Vector(type_code=Timestamp.type_code, items=column_data)
                table_values.append(vec)
            else:
                # Mixed types or complex types - keep as List
                table_values.append(column_data)

        self.ptr = FFI.init_table(columns=table_columns.ptr, values=table_values.ptr)

    def columns(self) -> Any:
        return utils.ray_to_python(FFI.get_table_keys(self.ptr))

    def values(self) -> Any:
        return utils.ray_to_python(FFI.get_table_values(self.ptr))

    def __str__(self) -> str:
        return FFI.repr_table(self.ptr)

    def __repr__(self) -> str:
        return f"Table[{self.columns()}]"

    def __eq__(self, eq: Any) -> bool:
        if isinstance(eq, _Table):
            return eq.columns() == self.columns() and eq.values() == self.values()
        return False


class Table:
    def __init__(
        self,
        name_or_data: str | None = None,
        columns: list[str] | None = None,
        values: list[Any] | None = None,
        ptr=None,
    ):
        if isinstance(name_or_data, str):
            self._table = name_or_data
            self._is_ref = True
        elif ptr is not None:
            self._table = _Table(ptr=ptr)
            self._is_ref = False
        elif columns and values:
            self._table = _Table(columns=columns, values=values)
            self._is_ref = False
        else:
            raise ValueError("Must provide either name, columns/values, or ptr")

    def __getattr__(self, name: str) -> Column:
        if name.startswith("_"):
            return object.__getattribute__(self, name)
        return Column(name, table=self)

    def select(self, *cols, **computed_cols) -> SelectQueryBuilder:
        builder = SelectQueryBuilder(table=self._table)
        return builder.select(*cols, **computed_cols)

    def where(self, condition: Expression | Callable) -> SelectQueryBuilder:
        builder = SelectQueryBuilder(table=self._table)
        return builder.where(condition)

    def by(self, *cols, **computed_cols) -> SelectQueryBuilder:
        builder = SelectQueryBuilder(table=self._table)
        return builder.by(*cols, **computed_cols)

    def concat(self, *others: Table) -> Table:
        result = self._table
        for other in others:
            other_table = other._table if isinstance(other, Table) else other
            expr = Expression(Operation.CONCAT, result, other_table)
            result = utils.eval_obj(expr.to_low_level())
        return Table(ptr=result._table.ptr)

    @staticmethod
    def concat_all(tables: list[Table]) -> Table:
        if not tables:
            raise ValueError("Must provide at least one table")
        return tables[0].concat(*tables[1:])

    def inner_join(self, other: Table, on: str | list[str]) -> Table:
        from raypy.types.containers import Vector, List
        from raypy.types.scalars import Symbol

        if isinstance(on, str):
            on = [on]

        join_keys = Vector(type_code=Symbol.type_code, items=on)
        other_table = other._table if isinstance(other, Table) else other
        self_table = self._table
        result = utils.eval_obj(
            List([Operation.IJ, join_keys, self_table, other_table])
        )

        return Table(ptr=result._table.ptr)

    def left_join(self, other: Table, on: str | list[str]) -> Table:
        from raypy.types.containers import Vector, List
        from raypy.types.scalars import Symbol

        if isinstance(on, str):
            on = [on]

        join_keys = Vector(type_code=Symbol.type_code, items=on)
        other_table = other._table if isinstance(other, Table) else other
        self_table = self._table
        result = utils.eval_obj(
            List([Operation.LJ, join_keys, self_table, other_table])
        )

        return Table(ptr=result._table.ptr)

    def window_join(
        self,
        on: list[str],
        join_with: list[Any],
        interval: TableColumnInterval,
        **aggregations,
    ) -> Table:
        return self._wj(
            method=Operation.WJ,
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
            method=Operation.WJ1,
            on=on,
            join_with=join_with,
            interval=interval,
            **aggregations,
        )

    def _wj(
        self,
        method: Operation,
        on: list[str],
        join_with: list[Any],
        interval: TableColumnInterval,
        **aggregations,
    ) -> Table:
        from raypy.types import Vector, Symbol

        agg_dict = {}
        for name, expr in aggregations.items():
            if isinstance(expr, Expression):
                agg_dict[name] = expr.to_low_level()
            elif isinstance(expr, Column):
                agg_dict[name] = expr.name
            else:
                agg_dict[name] = expr

        join_keys = Vector(type_code=Symbol.type_code, items=on)

        result = utils.eval_obj(
            List(
                [
                    method,
                    join_keys,
                    interval.compile(),
                    self._table,
                    *[t.ptr for t in join_with],
                    agg_dict,
                ]
            )
        )

        return Table(ptr=result._table.ptr)

    @property
    def ptr(self) -> r.RayObject:
        if isinstance(self._table, str):
            self._table = utils.eval_str(self._table)

        return self._table.ptr

    def update(self, **kwargs) -> UpdateQuery:
        return UpdateQuery(self._table, **kwargs)

    def insert(self, *args, **kwargs) -> InsertQuery:
        return InsertQuery(self._table, *args, **kwargs)

    def upsert(
        self,
        data: dict[str, Any] | list[dict[str | Any]],
        match_on: str | list[str] = "id",
    ) -> UpsertQuery:
        return UpsertQuery(self._table, data, match_on)

    def save(self, name: str) -> None:
        FFI.binary_set(FFI.init_symbol(name), self._table.ptr)

    def _get_table(self) -> _Table:
        if self._is_ref:
            return utils.eval_str(self._table)
        return self._table

    @property
    def columns(self) -> list[str]:
        if isinstance(self._table, _Table):
            cols = self._table.columns()
            return [col.value for col in cols]
        return []

    def values(self):
        if self._is_ref:
            table = utils.eval_str(self._table)
            return table.values()
        return self._table.values()

    @property
    def shape(self) -> tuple[int]:
        if isinstance(self._table, _Table):
            vals = self._table.values()
            rows = len(vals[0]) if vals and len(vals) > 0 else 0
            cols = len(self.columns)
            return (rows, cols)
        return (0, 0)

    def __len__(self) -> int:
        return self.shape[0]

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.__getattr__(key)
        elif isinstance(key, list):
            return self.select(*key).execute()
        else:
            raise NotImplementedError("Row/slice access not yet implemented")

    @classmethod
    def from_dict(cls, data: dict[str, list[Any]]) -> Table:
        columns = list(data.keys())
        values = list(data.values())
        return cls(columns=columns, values=values)

    @classmethod
    def from_csv(
        cls,
        column_types: list[RayObject],
        path: str,
    ) -> Table:
        query = List(
            [
                Operation.READ_CSV,
                Vector([c.ray_name for c in column_types], type_code=Symbol.type_code),
                String(path),
            ]
        )
        return utils.eval_obj(query)

    @classmethod
    def get(cls, name: str) -> Table:
        return cls(name)

    @staticmethod
    def _create_proxy(table: str | _Table) -> Table:
        proxy = object.__new__(Table)
        proxy._table = table
        proxy._is_ref = isinstance(table, str)
        return proxy

    def __str__(self) -> str:
        if isinstance(self._table, _Table):
            return FFI.repr_table(self._table.ptr)
        elif isinstance(self._table, str):
            table = utils.eval_str(self._table)
            return FFI.repr_table(table._table.ptr)
        return f"Table('{self._table}')"

    def __repr__(self) -> str:
        if self._is_ref:
            return f"Table('{self._table}')"
        return f"Table(columns={self.columns})"

    def xasc(self, *cols) -> Table:
        from raypy.types import List, Vector, Symbol

        return utils.eval_obj(
            List(
                [Operation.XASC, self._table, Vector(cols, type_code=-Symbol.type_code)]
            )
        )

    def xdesc(self, *cols) -> Table:
        from raypy.types import List, Vector, Symbol

        return utils.eval_obj(
            List(
                [
                    Operation.XDESC,
                    self._table,
                    Vector(cols, type_code=-Symbol.type_code),
                ]
            )
        )


class SelectQuery:
    """
    Query to perform select operation.
    """

    ptr: r.RayObject

    def __validate(
        self,
        attributes: dict[str, str | Expression | dict[str, str]],
        select_from: str | SelectQuery | _Table,
        where: Expression | None = None,
    ) -> None:
        self.attr_keys = attributes.keys()
        self.attr_values = attributes.values()

        if not select_from:
            raise ValueError("Attribute select_from is required.")

        if where is not None:
            if not isinstance(where, _Expression):
                raise ValueError("Attribute where should be an Expression.")

        if any([not isinstance(key, str) for key in self.attr_keys]):
            raise ValueError("Query keys should be Python strings.")

        self.attributes = attributes
        self.select_from = select_from
        self.where = where

    def __build_query(self) -> None:
        from raypy.types.scalars import Symbol

        length = len(self.attr_keys) + 1 if not self.where else len(self.attr_keys) + 2
        self._query_keys = FFI.init_vector(type_code=Symbol.type_code, length=length)
        self._query_values = FFI.init_list()

        for idx, key in enumerate(self.attr_keys):
            # Fill query keys with requested attributes
            FFI.insert_obj(
                insert_to=self._query_keys,
                idx=idx,
                ptr=utils.python_to_ray(key),
            )
        else:
            # Push "from" keyword to query keys
            FFI.insert_obj(
                insert_to=self._query_keys,
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
                insert_to=self._query_keys,
                idx=len(self.attr_keys) + 1,
                ptr=utils.python_to_ray("where"),
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
        from raypy.types.containers import Dict

        return str(Dict(ptr=self.ptr))

    def __repr__(self) -> str:
        return self.__str__()


class SelectQueryBuilder:
    def __init__(
        self,
        table: str | _Table,
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
                    attributes[name] = expr.to_low_level()
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
            where_expr = combined.to_low_level()

        if self._by_cols:
            by_attributes = {}
            cols, computed = self._by_cols

            for col in cols:
                by_attributes[col] = col

            for name, expr in computed.items():
                if isinstance(expr, Expression):
                    by_attributes[name] = expr.to_low_level()
                elif isinstance(expr, Column):
                    by_attributes[name] = expr.name
                else:
                    by_attributes[name] = expr

            attributes["by"] = by_attributes

        return SelectQuery(
            select_from=self._table, attributes=attributes, where=where_expr
        )

    def _convert_expr(self, expr: Expression | Column) -> _Expression | str:
        if isinstance(expr, Expression):
            return expr.to_low_level()
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
    """
    Query to perform update operation
    """

    ptr: r.RayObject

    def __init__(self, table: str | Table, **attributes):
        self._table = table
        self._attributes = attributes
        self._where_condition = None

    def __validate(
        self,
        update_from: str | SelectQuery | Expression | _Table,
        attributes: dict[str, str | Expression],
        where: Expression | None = None,
    ) -> None:
        self.attr_keys = attributes.keys()
        self.attr_values = attributes.values()

        if not update_from:
            raise ValueError("Attribute update_from is required.")

        if where is not None:
            if not isinstance(where, _Expression):
                raise ValueError("Attribute where should be an Expression.")

        self.attributes = attributes
        self.update_from = update_from
        self._where = where

    def __build_query(self) -> r.RayObject:
        from raypy.types.scalars import Symbol

        length = len(self.attr_keys) + 1 if not self._where else len(self.attr_keys) + 2
        self._query_keys = FFI.init_vector(type_code=Symbol.type_code, length=length)
        self._query_values = FFI.init_list()

        for idx, key in enumerate(self.attr_keys):
            # Fill query keys with requested attributes
            FFI.insert_obj(
                insert_to=self._query_keys,
                idx=idx,
                ptr=utils.python_to_ray(key),
            )
        else:
            # Push "from" keyword to query keys
            FFI.insert_obj(
                insert_to=self._query_keys,
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
            if isinstance(self.update_from, str):
                from raypy.types.scalars import QuotedSymbol

                key = QuotedSymbol(self.update_from)
                FFI.push_obj(iterable=self._query_values, ptr=key.ptr)
            else:
                FFI.push_obj(
                    iterable=self._query_values,
                    ptr=utils.python_to_ray(self.update_from),
                )

        if self._where is not None:
            FFI.insert_obj(
                insert_to=self._query_keys,
                idx=len(self.attr_keys) + 1,
                ptr=utils.python_to_ray("where"),
            )
            FFI.push_obj(
                iterable=self._query_values,
                ptr=self._where.ptr,
            )

        self.ptr = FFI.init_dict(self._query_keys, self._query_values)

    def where(self, condition: Expression | Callable) -> UpdateQuery:
        if callable(condition):
            temp = Table._create_proxy(self._table)
            condition = condition(temp)
        self._where_condition = condition
        return self

    def execute(self) -> Table | bool | str:
        where_expr = None
        if self._where_condition:
            if isinstance(self._where_condition, Expression):
                where_expr = self._where_condition.to_low_level()
            else:
                where_expr = self._where_condition

        converted_attrs = {}
        for key, value in self._attributes.items():
            if isinstance(value, Expression):
                converted_attrs[key] = value.to_low_level()
            elif isinstance(value, Column):
                converted_attrs[key] = value.name
            elif isinstance(value, DictLookup):
                converted_attrs[key] = value.to_low_level()
            else:
                converted_attrs[key] = value

        self.__validate(
            update_from=self._table,
            attributes=converted_attrs,
            where=where_expr,
        )
        self.__build_query()

        return utils.ray_to_python(FFI.update(query=self.ptr))

    def __repr__(self) -> str:
        return f"UpdateQuery(set={list(self._attributes.keys())}, where={self._where_condition is not None})"


class InsertQuery:
    def __init__(self, table: str | Table, *args, **kwargs):
        self._table = table

        if args:
            self._insertable = args[0] if len(args) == 1 else list(args)
        elif kwargs:
            self._insertable = list(kwargs.values())
        else:
            raise ValueError("No data to insert")

    def __validate(
        self,
        insert_to: str | _Table,
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
                ptr=utils.python_to_ray(attribute),
            )

        self.insert_to_ptr = utils.python_to_ray(self.insert_to)

    def execute(self) -> Table:
        self.__validate(insert_to=self._table, insertable=self._insertable)
        self.__build_query()

        return utils.ray_to_python(
            FFI.insert(table_obj=self.insert_to_ptr, data_obj=self.insertable_ptr)
        )

    def __repr__(self) -> str:
        return f"InsertQuery({len(self._insertable)} values)"


class UpsertQuery:
    def __init__(
        self,
        table: str | _Table,
        data: dict[str, Any] | list[dict[str, Any]],
        match_on: str | list[str],
    ):
        self._table = table
        self._data = data if isinstance(data, list) else [data]
        self._match_by_first = 1 if isinstance(match_on, str) else len(match_on)

    def __validate(
        self,
        upsert_to: str | _Table,
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
        from raypy.types.containers import Vector
        from raypy.types.scalars import Symbol, I64, F64, B8, QuotedSymbol

        # Match low-level is a number of ordered fields provided in upsertable.
        self.match_ptr = FFI.init_i64(self.match_by_first)

        i_keys = FFI.init_vector(type_code=-r.TYPE_SYMBOL, length=len(self.upsertable))
        for idx, key in enumerate(self.upsertable.keys()):  # type: ignore
            FFI.insert_obj(
                insert_to=i_keys,
                idx=idx,
                ptr=QuotedSymbol(key).ptr,
                # ptr=utils.python_to_ray(key),
            )

        i_values = FFI.init_list()
        for column_data in self.upsertable.values():  # type: ignore
            # Convert to appropriate Vector type (like Table.__init__ does)
            if not column_data:
                FFI.push_obj(iterable=i_values, ptr=FFI.init_list())
            elif all(isinstance(x, str) for x in column_data):
                # String column -> Vector of Symbols
                vec = Vector(type_code=Symbol.type_code, items=column_data)
                FFI.push_obj(iterable=i_values, ptr=vec.ptr)
            elif all(
                isinstance(x, (int, float)) and not isinstance(x, bool)
                for x in column_data
            ):
                # Numeric column -> detect if int or float
                if all(isinstance(x, int) for x in column_data):
                    vec = Vector(type_code=I64.type_code, items=column_data)
                else:
                    vec = Vector(type_code=F64.type_code, items=column_data)
                FFI.push_obj(iterable=i_values, ptr=vec.ptr)
            elif all(isinstance(x, bool) for x in column_data):
                # Boolean column
                vec = Vector(type_code=B8.type_code, items=column_data)
                FFI.push_obj(iterable=i_values, ptr=vec.ptr)
            else:
                # Mixed types - keep as List
                _l = FFI.init_list()
                for value in column_data:
                    FFI.push_obj(iterable=_l, ptr=utils.python_to_ray(value))
                FFI.push_obj(iterable=i_values, ptr=_l)

        self.upsertable_ptr = FFI.init_dict(i_keys, i_values)

        if isinstance(self.upsert_to, _Table):
            self.upsert_to_ptr = self.upsert_to.ptr
        else:
            from raypy.types.scalars import QuotedSymbol

            self.upsert_to_ptr = QuotedSymbol(self.upsert_to).ptr

    def execute(self) -> Table:
        upsertable = {}
        for row in self._data:
            for key, value in row.items():
                if key not in upsertable:
                    upsertable[key] = []
                upsertable[key].append(value)

        self.__validate(
            upsert_to=self._table,
            match_by_first=self._match_by_first,
            upsertable=upsertable,
        )
        self.__build_query()
        return utils.ray_to_python(
            FFI.upsert(
                table_obj=self.upsert_to_ptr,
                keys_obj=self.match_ptr,
                data_obj=self.upsertable_ptr,
            )
        )

    def __repr__(self) -> str:
        return f"UpsertQuery({len(self._data)} rows, match_by_first={self._match_by_first})"


class DictLookup(Expression):
    def __init__(self, dict_obj, key: Column | str):
        self.dict_obj = dict_obj
        self.key = key.name if isinstance(key, Column) else key
        super().__init__(Operation.AT, dict_obj, self.key)


def lookup(dict_obj, column: Column | str) -> DictLookup:
    return DictLookup(dict_obj, column)


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
        from raypy.types import Vector, I64, QuotedSymbol

        return List(
            [
                Operation.MAP_LEFT,
                Operation.ADD,
                Vector([self.lower, self.upper], type_code=I64.type_code),
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
    "FilteredColumn",
    "SelectQueryBuilder",
    "UpdateQuery",
    "InsertQuery",
    "UpsertQuery",
    "DictLookup",
    "lookup",
    "TableColumnInterval",
]

TypeRegistry.register(type_code=r.TYPE_TABLE, type_class=Table)
