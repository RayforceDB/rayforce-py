from __future__ import annotations

from collections.abc import Iterable
from functools import wraps
import typing as t

from rayforce import _rayforce_c as r
from rayforce import utils
from rayforce.core import FFI
from rayforce.types import (
    C8,
    I64,
    Dict,
    List,
    QuotedSymbol,
    String,
    Symbol,
    Vector,
    exceptions,
)
from rayforce.types.base import RayObject
from rayforce.types.operators import Operation
from rayforce.types.registry import TypeRegistry


class _TableProtocol(t.Protocol):
    _ptr: r.RayObject | str
    is_reference: bool

    @property
    def ptr(self) -> r.RayObject: ...


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
            raise TypeError("is_ argument has to be bool")
        if other is True:
            return Expression(Operation.EVAL, self)
        return Expression(Operation.EVAL, Expression(Operation.NOT, self))

    def isin(self, values: list[t.Any] | RayObject) -> Expression:
        if isinstance(values, RayObject):
            return Expression(Operation.IN, self, values)

        if all(isinstance(x, type(values[0])) for x in values):
            return Expression(
                Operation.IN,
                self,
                Vector(
                    items=values,
                    ray_type=utils.python_to_ray(values[0]).get_obj_type(),
                ),
            )

        return Expression(Operation.IN, self, Expression(Operation.LIST, *values))


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

    def __eq__(self, other) -> Expression:  # type: ignore[override]
        return Expression(Operation.EQUALS, self, other)

    def __ne__(self, other) -> Expression:  # type: ignore[override]
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
        converted_operands: list[t.Any] = []
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
    _ptr: r.RayObject | str
    type_code: int

    def __init__(
        self,
        ptr: r.RayObject | str,
    ) -> None:
        self._ptr = ptr
        self.is_reference = isinstance(ptr, str)

    @classmethod
    def from_ptr(cls, ptr: r.RayObject) -> t.Self:
        if (_type := ptr.get_obj_type()) != cls.type_code:
            raise ValueError(f"Expected RayForce object of type {cls.type_code}, got {_type}")
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
                columns=Vector(items=items.keys(), ray_type=Symbol).ptr,  # type: ignore[arg-type]
                values=List(items.values()).ptr,
            ),
        )

    @property
    def ptr(self) -> r.RayObject:
        if isinstance(self._ptr, str):
            return QuotedSymbol(self._ptr).ptr
        return self._ptr

    @property
    def evaled_ptr(self) -> r.RayObject:
        if isinstance(self._ptr, str):
            return utils.eval_str(self._ptr).ptr
        return self._ptr

    @classmethod
    def from_splayed(cls, path: str, symfile: str | None = None) -> Table:
        _args = [FFI.init_string(path)]
        if symfile is not None:
            _args.append(FFI.init_string(symfile))
        _tbl = utils.eval_obj(List([Operation.GET_SPLAYED, *_args]))
        _tbl.is_parted = True
        return _tbl

    @classmethod
    def from_parted(cls, path: str, symfile: str) -> Table:
        _args = [FFI.init_string(path)]
        if symfile is not None:
            _args.append(QuotedSymbol(symfile).ptr)
        _tbl = utils.eval_obj(List([Operation.GET_PARTED, *_args]))
        _tbl.is_parted = True
        return _tbl


class TableIOMixin:
    _ptr: r.RayObject | str

    if t.TYPE_CHECKING:

        @property
        def ptr(self) -> r.RayObject: ...

        @property
        def evaled_ptr(self) -> r.RayObject: ...

    def save(self, name: str) -> None:
        FFI.binary_set(FFI.init_symbol(name), self.ptr)

    def set_splayed(self, path: str, symlink: str | None = None) -> None:
        _args = [FFI.init_string(path), self.evaled_ptr]
        if symlink is not None:
            _args.append(FFI.init_string(symlink))
        utils.eval_obj(List([Operation.SET_SPLAYED, *_args]))

    def set_csv(self, path: str, separator: str | None = None) -> None:
        _args = [FFI.init_string(path), self.evaled_ptr]
        if separator is not None:
            _args.append(C8(separator).ptr)
        utils.eval_obj(List([Operation.WRITE_CSV, *_args]))


class DestructiveOperationHandler:
    def __call__(self, func: t.Callable) -> t.Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.is_parted:
                raise exceptions.PartedTableError(
                    "use .select() first. Unable to use destructive operation on a parted table."
                )
            return func(self, *args, **kwargs)

        return wrapper


class TableValueAccessorMixin:
    _ptr: r.RayObject | str
    is_parted: bool

    if t.TYPE_CHECKING:
        is_reference: bool

        @property
        def evaled_ptr(self) -> r.RayObject: ...

        @property
        def ptr(self) -> r.RayObject: ...

    def columns(self) -> Vector:
        return utils.ray_to_python(FFI.get_table_keys(self.evaled_ptr))

    @DestructiveOperationHandler()
    def values(self) -> List:
        return utils.ray_to_python(FFI.get_table_values(self.evaled_ptr))


class TableReprMixin:
    _ptr: r.RayObject | str

    if t.TYPE_CHECKING:

        def columns(self) -> Vector: ...

    def __str__(self) -> str:
        if isinstance(self._ptr, str):
            return self._ptr

        return FFI.repr_table(self._ptr)

    def __repr__(self) -> str:
        if isinstance(self._ptr, str):
            return f"TableReference['{self._ptr}']"
        return f"Table{self.columns()}"


class TableOrderByMixin:
    _ptr: r.RayObject | str

    if t.TYPE_CHECKING:

        @property
        def evaled_ptr(self) -> r.RayObject: ...

    def xasc(self, *cols: Column) -> Table:
        _cols = [c.name for c in cols]
        return utils.eval_obj(
            List([Operation.XASC, self.evaled_ptr, Vector(_cols, ray_type=Symbol)])
        )

    def xdesc(self, *cols: Column) -> Table:
        _cols = [c.name for c in cols]
        return utils.eval_obj(
            List([Operation.XDESC, self.evaled_ptr, Vector(_cols, ray_type=Symbol)])
        )


class TableQueryMixin:
    _ptr: r.RayObject | str

    if t.TYPE_CHECKING:
        is_reference: bool

        @property
        def ptr(self) -> r.RayObject: ...

    def select(self, *cols, **computed_cols) -> SelectQuery:
        return SelectQuery(table=self).select(*cols, **computed_cols)

    def where(self, condition: Expression) -> SelectQuery:
        return SelectQuery(table=self).where(condition)

    def by(self, *cols, **computed_cols) -> SelectQuery:
        return SelectQuery(table=self).by(*cols, **computed_cols)

    def update(self, **kwargs) -> UpdateQuery:
        return UpdateQuery(self, **kwargs)

    def insert(self, *args, **kwargs) -> InsertQuery:
        return InsertQuery(self, *args, **kwargs)

    def upsert(self, *args, match_by_first: int, **kwargs) -> UpsertQuery:
        return UpsertQuery(self, *args, match_by_first=match_by_first, **kwargs)

    def concat(self, *others: Table) -> Table:
        result: Table = self  # type: ignore[assignment]
        for other in others:
            expr = Expression(Operation.CONCAT, result.ptr, other.ptr)
            result = t.cast("Table", utils.eval_obj(expr.compile()))
        return result

    def inner_join(self, other: Table, on: str | list[str]) -> Table:
        return self._join(other=other, on=on, type_=Operation.INNER_JOIN)

    def left_join(self, other: Table, on: str | list[str]) -> Table:
        return self._join(other=other, on=on, type_=Operation.LEFT_JOIN)

    def window_join(
        self,
        on: list[str],
        join_with: list[t.Any],
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
        join_with: list[t.Any],
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

        agg_dict: dict[str, t.Any] = {}
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


class Table(
    TableInitMixin,
    TableValueAccessorMixin,
    TableReprMixin,
    TableQueryMixin,
    TableOrderByMixin,
    TableIOMixin,
):
    type_code = r.TYPE_TABLE
    _ptr: r.RayObject | str
    is_reference: bool
    is_parted: bool = False


class SelectQuery:
    def __init__(
        self,
        table: _TableProtocol,
        select_cols: tuple[t.Any, t.Any] | None = None,
        where_conditions: list[Expression] | None = None,
        by_cols: tuple[tuple[t.Any, ...], dict[str, t.Any]] | None = None,
    ):
        self.table = table
        self._select_cols = select_cols
        self._where_conditions = where_conditions or []
        self._by_cols: tuple[tuple[t.Any, ...], dict[str, t.Any]] = (
            by_cols if by_cols is not None else ((), {})
        )
        self._ptr: r.RayObject | None = None

    def select(self, *cols, **computed_cols) -> SelectQuery:
        return SelectQuery(
            table=self.table,
            select_cols=(cols, computed_cols),
            where_conditions=self._where_conditions,
            by_cols=self._by_cols,
        )

    def where(self, condition: Expression) -> SelectQuery:
        new_conditions = self._where_conditions.copy()
        new_conditions.append(condition)
        return SelectQuery(
            table=self.table,
            select_cols=self._select_cols,
            where_conditions=new_conditions,
            by_cols=self._by_cols,
        )

    def by(self, *cols, **computed_cols) -> SelectQuery:
        return SelectQuery(
            table=self.table,
            select_cols=self._select_cols,
            where_conditions=self._where_conditions,
            by_cols=(cols, computed_cols),
        )

    @property
    def ptr(self) -> r.RayObject:
        if self._ptr is None:
            self._ptr = self._build_query_ptr()
        return self._ptr

    def execute(self) -> Table:
        return utils.ray_to_python(FFI.select(query=self.ptr))

    def _build_query_ptr(self) -> r.RayObject:
        attributes = {}
        if self._select_cols:
            cols, computed = self._select_cols
            attributes = {col: col for col in cols if col != "*"}

            for name, expr in computed.items():
                if isinstance(expr, Expression):
                    attributes[name] = expr.compile()
                elif isinstance(expr, Column):
                    attributes[name] = expr.name
                else:
                    attributes[name] = expr

        where_expr = None
        if self._where_conditions:
            combined = self._where_conditions[0]
            for cond in self._where_conditions[1:]:
                combined = combined & cond
            where_expr = combined

        if self._by_cols and (self._by_cols[0] or self._by_cols[1]):
            cols, computed = self._by_cols
            by_attributes = {col: col for col in cols}

            for name, expr in computed.items():
                if isinstance(expr, Expression):
                    by_attributes[name] = expr.compile()
                elif isinstance(expr, Column):
                    by_attributes[name] = expr.name
                else:
                    by_attributes[name] = expr
            attributes["by"] = by_attributes

        query_items = dict(attributes)

        if isinstance(self.table, Table):
            if self.table.is_reference:
                query_items["from"] = Symbol(self.table._ptr).ptr
            else:
                query_items["from"] = self.table.ptr
        else:
            query_items["from"] = utils.python_to_ray(self.table)

        if where_expr is not None:
            if isinstance(where_expr, Expression):
                query_items["where"] = where_expr.compile()
            else:
                query_items["where"] = where_expr

        return Dict(query_items).ptr


class UpdateQuery:
    def __init__(self, table: _TableProtocol, **attributes):
        self.table = table
        self.attributes = attributes
        self.where_condition: Expression | None = None

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

        converted_attrs: dict[str, t.Any] = {}
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
    def __init__(self, table: _TableProtocol, *args, **kwargs):
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

            if isinstance(first_val, Iterable) and not isinstance(first_val, (str, bytes)):
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
        cloned_table = FFI.quote(self.table.ptr)
        new_table = FFI.insert(
            table=cloned_table,
            data=self.insertable_ptr,
        )
        if self.table.is_reference:
            return Table.from_name(Symbol(ptr=new_table).value)
        return Table.from_ptr(new_table)


class UpsertQuery:
    def __init__(self, table: _TableProtocol, *args, match_by_first: int, **kwargs) -> None:
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

            if isinstance(first_val, Iterable) and not isinstance(first_val, (str, bytes)):
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
        cloned_table = FFI.quote(self.table.ptr)
        new_table = FFI.upsert(
            table=cloned_table,
            keys=self._match_by_first.ptr,
            data=self.upsertable_ptr,
        )
        if self.table.is_reference:
            return Table.from_name(Symbol(ptr=new_table).value)
        return Table.from_ptr(new_table)


class TableColumnInterval:
    def __init__(
        self,
        lower: int,
        upper: int,
        table: Table,
        column: str | Column,
    ) -> None:
        self.lower = lower
        self.upper = upper
        self.table = table
        self.column = column

    def compile(self) -> List:
        return List(
            [
                Operation.MAP_LEFT,
                Operation.ADD,
                Vector([self.lower, self.upper], ray_type=I64),
                List(
                    [
                        Operation.AT,
                        self.table.ptr,
                        QuotedSymbol(
                            self.column.name if isinstance(self.column, Column) else self.column
                        ),
                    ]
                ),
            ]
        )


__all__ = [
    "Column",
    "Expression",
    "InsertQuery",
    "Table",
    "TableColumnInterval",
    "UpdateQuery",
    "UpsertQuery",
]

TypeRegistry.register(type_code=r.TYPE_TABLE, type_class=Table)  # type: ignore[arg-type]
