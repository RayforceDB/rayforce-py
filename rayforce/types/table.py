from __future__ import annotations

from collections.abc import Iterable
from functools import wraps
import typing as t

from rayforce import _rayforce_c as r
from rayforce import errors, utils
from rayforce.ffi import FFI
from rayforce.types import (
    C8,
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
from rayforce.types.registry import TypeRegistry

if t.TYPE_CHECKING:
    from rayforce.types.fn import Fn


class _TableProtocol(t.Protocol):
    _ptr: r.RayObject | str
    is_reference: bool
    is_parted: bool

    @property
    def ptr(self) -> r.RayObject: ...

    @property
    def evaled_ptr(self) -> r.RayObject: ...

    def columns(self) -> Vector: ...


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
                    ray_type=FFI.get_obj_type(utils.python_to_ray(values[0])),
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
    def __init__(self, operation: Operation | Fn, *operands: t.Any) -> None:
        self.operation = operation
        self.operands = operands

    def compile(self, *, ipc: bool = False) -> r.RayObject:
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
                converted_operands.append(operand.compile(ipc=ipc))
            elif isinstance(operand, Column):
                converted_operands.append(operand.name)
            elif hasattr(operand, "ptr"):
                converted_operands.append(operand)
            elif isinstance(operand, str):
                converted_operands.append(List([Operation.QUOTE, operand]).ptr)
            else:
                converted_operands.append(operand)
        # Convert operation to its primitive if it's an Operation enum
        operation_obj = (
            self.operation.primitive if isinstance(self.operation, Operation) else self.operation
        )
        return List([operation_obj, *converted_operands]).ptr

    def execute(self) -> t.Any:
        return utils.eval_obj(self.compile())


class Column(AggregationMixin, OperatorMixin):
    def __init__(self, name: str, table: Table | None = None):
        self.name = name
        self.table = table

    def where(self, condition: Expression) -> Expression:
        return Expression(Operation.MAP, self, condition)


class TableInitMixin:
    _ptr: r.RayObject | str
    type_code: int

    def __init__(self, ptr: r.RayObject | str | dict[str, Vector]) -> None:
        if isinstance(ptr, dict):
            self._ptr, self.is_reference = (
                FFI.init_table(
                    columns=Vector(items=ptr.keys(), ray_type=Symbol).ptr,  # type: ignore[arg-type]
                    values=List(ptr.values()).ptr,
                ),
                False,
            )
            return
        if isinstance(ptr, r.RayObject):
            if (_type := FFI.get_obj_type(ptr)) != self.type_code:
                raise errors.RayforceInitError(
                    f"Expected RayForce object of type {self.type_code}, got {_type}"
                )
            self._ptr, self.is_reference = ptr, False
            return
        if isinstance(ptr, str):
            self._ptr, self.is_reference = ptr, True
            return

        raise errors.RayforceInitError(f"Unable to initialize Table from {type(ptr)}")

    @classmethod
    def from_ptr(cls, ptr: r.RayObject) -> t.Self:
        return cls(ptr)

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
    def from_parted(cls, path: str, name: str) -> Table:
        _args = [FFI.init_string(path)]
        if name is not None:
            _args.append(QuotedSymbol(name).ptr)
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

    def ipcsave(self, name: str) -> Expression:
        return Expression(Operation.SET, name, self.ptr)

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
                raise errors.RayforcePartedTableError(
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

    @DestructiveOperationHandler()
    def at_column(self, column_name: str) -> Vector | List:
        if not isinstance(column_name, str):
            raise errors.RayforceConversionError("Column name has to be a string")
        return utils.eval_obj(List([Operation.AT, self.evaled_ptr, QuotedSymbol(column_name)]))

    @DestructiveOperationHandler()
    def at_row(self, row_n: int) -> Dict:
        if not isinstance(row_n, int):
            raise errors.RayforceConversionError("Row number has to an integer")
        return utils.eval_obj(List([Operation.AT, self.evaled_ptr, I64(row_n)]))

    @DestructiveOperationHandler()
    def take(self, n: int, offset: int = 0) -> Table:
        if not isinstance(n, int) or not isinstance(offset, int):
            raise errors.RayforceConversionError("Number of rows has to be an integer")

        args: int | Vector = n
        if offset != 0:
            args = Vector(items=[offset, n], ray_type=I64)

        return utils.eval_obj(List([Operation.TAKE, self.evaled_ptr, args]))

    def columns(self) -> Vector:
        return utils.ray_to_python(FFI.get_table_keys(self.evaled_ptr))

    @DestructiveOperationHandler()
    def values(self) -> List:
        return utils.ray_to_python(FFI.get_table_values(self.evaled_ptr))

    @DestructiveOperationHandler()
    def shape(self) -> tuple[int, int]:
        rows = utils.eval_obj(
            List([Operation.COUNT, [Operation.AT, [Operation.VALUE, self.evaled_ptr], 0]])
        )
        cols = utils.eval_obj(List([Operation.COUNT, [Operation.KEY, self.evaled_ptr]]))
        return (rows, cols)

    @DestructiveOperationHandler()
    def __len__(self) -> int:
        return utils.eval_obj(
            List([Operation.COUNT, [Operation.AT, [Operation.VALUE, self.evaled_ptr], 0]])
        ).value

    @DestructiveOperationHandler()
    def __getitem__(self, key: str | list[str]) -> Vector | List | Table:
        if isinstance(key, str):
            return self.at_column(key)
        if isinstance(key, list):
            return t.cast("Table", self).select(*key).execute()
        raise errors.RayforceConversionError(
            f"Key must be a string or list of strings, got {type(key).__name__}"
        )

    @DestructiveOperationHandler()
    def head(self, n: int = 5) -> Table:
        return t.cast("Table", self).take(n)

    @DestructiveOperationHandler()
    def tail(self, n: int = 5) -> Table:
        return t.cast("Table", self).take(-n)

    @DestructiveOperationHandler()
    def describe(self) -> dict[str, dict[str, t.Any]]:
        stats: dict[str, dict[str, t.Any]] = {}
        columns, values = self.columns(), self.values()

        numeric_types = {r.TYPE_I64, r.TYPE_I32, r.TYPE_I16, r.TYPE_F64, r.TYPE_U8}

        def _extract(val: t.Any) -> t.Any:
            return val.value if hasattr(val, "value") else val

        for i, col_name in enumerate(columns):
            col_vector = values[i]
            if not col_vector:
                continue

            if FFI.get_obj_type(col_vector.ptr) not in numeric_types:
                continue

            name = col_name.value if hasattr(col_name, "value") else str(col_name)

            stats[name] = {
                "count": _extract(utils.eval_obj(List([Operation.COUNT, col_vector.ptr]))),
                "mean": _extract(utils.eval_obj(List([Operation.AVG, col_vector.ptr]))),
                "min": _extract(utils.eval_obj(List([Operation.MIN, col_vector.ptr]))),
                "max": _extract(utils.eval_obj(List([Operation.MAX, col_vector.ptr]))),
            }

        return stats

    @property
    def dtypes(self) -> dict[str, str]:
        meta = utils.eval_obj(
            List([Operation.AS, [Operation.QUOTE, "DICT"], [Operation.META, self.evaled_ptr]])
        )
        names, types = meta["name"], meta["type"]

        return {
            (n.value if hasattr(n, "value") else str(n)): t.value if hasattr(t, "value") else str(t)
            for n, t in zip(names, types, strict=True)
        }

    @DestructiveOperationHandler()
    def drop(self, *cols: str) -> Table:
        current_cols = {c.value if hasattr(c, "value") else str(c) for c in self.columns()}
        cols_to_drop = set(cols)
        if unknown := (cols_to_drop - current_cols):
            raise errors.RayforceConversionError(f"Columns not found: {', '.join(sorted(unknown))}")
        if keep := [c for c in current_cols if c not in cols_to_drop]:
            return t.cast("Table", self).select(*keep).execute()
        raise errors.RayforceConversionError("Cannot drop all columns")

    @DestructiveOperationHandler()
    def rename(self, mapping: dict[str, str]) -> Table:
        current_cols = [c.value if hasattr(c, "value") else str(c) for c in self.columns()]
        unknown = set(mapping.keys()) - set(current_cols)
        if unknown:
            raise errors.RayforceConversionError(f"Columns not found: {', '.join(sorted(unknown))}")

        select_args = {}
        for col in current_cols:
            new_name = mapping.get(col, col)
            select_args[new_name] = Column(col)

        return t.cast("Table", self).select(**select_args).execute()

    def cast(self, column: str, to_type: type) -> Table:
        current_cols = [c.value if hasattr(c, "value") else str(c) for c in self.columns()]
        if column not in current_cols:
            raise errors.RayforceConversionError(f"Column not found: {column}")

        if not hasattr(to_type, "ray_name"):
            raise errors.RayforceConversionError(
                f"Invalid target type: {to_type}. Must be a Rayforce type like I64, F64, Symbol."
            )

        select_args: dict[str, Expression | Column] = {}
        for col in current_cols:
            if col == column:
                select_args[col] = Expression(
                    Operation.AS,
                    QuotedSymbol(to_type.ray_name.lower()),
                    Column(col),
                )
            else:
                select_args[col] = Column(col)

        return t.cast("Table", self).select(**select_args).execute()


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


class TableQueryMixin:
    _ptr: r.RayObject | str

    if t.TYPE_CHECKING:
        is_reference: bool

        @property
        def ptr(self) -> r.RayObject: ...

    def select(self, *cols, **computed_cols) -> SelectQuery:
        return SelectQuery(table=t.cast("_TableProtocol", self)).select(*cols, **computed_cols)

    def where(self, condition: Expression) -> SelectQuery:
        return SelectQuery(table=t.cast("_TableProtocol", self)).where(condition)

    def by(self, *cols, **computed_cols) -> SelectQuery:
        return SelectQuery(table=t.cast("_TableProtocol", self)).by(*cols, **computed_cols)

    def update(self, **kwargs) -> UpdateQuery:
        return UpdateQuery(t.cast("_TableProtocol", self), **kwargs)

    def insert(self, *args, **kwargs) -> InsertQuery:
        return InsertQuery(t.cast("_TableProtocol", self), *args, **kwargs)

    def upsert(self, *args, key_columns: int, **kwargs) -> UpsertQuery:
        return UpsertQuery(t.cast("_TableProtocol", self), *args, key_columns=key_columns, **kwargs)

    def order_by(self, *cols: Column | str, desc: bool = False) -> SelectQuery:
        return SelectQuery(table=t.cast("_TableProtocol", self)).order_by(*cols, desc=desc)

    def concat(self, *others: _TableProtocol) -> Table:
        result: _TableProtocol = t.cast("_TableProtocol", self)
        for other in others:
            expr = Expression(Operation.CONCAT, result.ptr, other.ptr)
            result = t.cast("Table", utils.eval_obj(expr.compile()))
        return t.cast("Table", result)

    def inner_join(self, other: _TableProtocol, on: str | list[str]) -> InnerJoin:
        return InnerJoin(t.cast("_TableProtocol", self), other, on)

    def left_join(self, other: _TableProtocol, on: str | list[str]) -> LeftJoin:
        return LeftJoin(t.cast("_TableProtocol", self), other, on)

    def asof_join(self, other: _TableProtocol, on: str | list[str]) -> AsofJoin:
        return AsofJoin(t.cast("_TableProtocol", self), other, on)

    def window_join(
        self,
        on: list[str],
        join_with: list[t.Any],
        interval: TableColumnInterval,
        **aggregations,
    ) -> WindowJoin:
        return WindowJoin(t.cast("_TableProtocol", self), on, join_with, interval, **aggregations)

    def window_join1(
        self,
        on: list[str],
        join_with: list[t.Any],
        interval: TableColumnInterval,
        **aggregations,
    ) -> WindowJoin1:
        return WindowJoin1(t.cast("_TableProtocol", self), on, join_with, interval, **aggregations)

    def pivot(
        self,
        index: str | list[str],
        columns: str,
        values: str,
        aggfunc: t.Literal["sum", "count", "avg", "min", "max", "first", "last"],
    ) -> PivotQuery:
        return PivotQuery(t.cast("_TableProtocol", self), index, columns, values, aggfunc)

    def sql(self, query: str) -> Table:
        from rayforce.plugins.sql import sql_query

        return sql_query(t.cast("Table", self), query)


class Table(
    TableInitMixin,
    TableValueAccessorMixin,
    TableReprMixin,
    TableQueryMixin,
    TableIOMixin,
):
    type_code = r.TYPE_TABLE
    _ptr: r.RayObject | str
    is_reference: bool
    is_parted: bool = False


class IPCQueryMixin:
    if t.TYPE_CHECKING:

        @property
        def ipc(self) -> r.RayObject: ...

    def ipcsave(self, name: str) -> Expression:
        return Expression(Operation.SET, name, self.ipc)


class _Join(IPCQueryMixin):
    type_: t.Literal[
        Operation.LEFT_JOIN
        | Operation.INNER_JOIN
        | Operation.ASOF_JOIN
        | Operation.WINDOW_JOIN
        | Operation.WINDOW_JOIN1
    ]

    def __init__(self, table: _TableProtocol, other: _TableProtocol, on: str | list[str]) -> None:
        self.table = table
        self.other = other
        self.on = on

    def compile(self) -> tuple[r.RayObject, ...]:
        on = self.on
        if isinstance(self.on, str):
            on = [self.on]
        return Vector(items=on, ray_type=Symbol).ptr, self.table.ptr, self.other.ptr

    @property
    def ipc(self) -> r.RayObject:
        return Expression(self.type_, *self.compile()).compile()

    def execute(self) -> Table:
        return utils.eval_obj(List([self.type_, *self.compile()]))


class _WindowJoin(_Join):
    def __init__(
        self,
        table: _TableProtocol,
        on: list[str],
        join_with: list[t.Any],
        interval: TableColumnInterval,
        **aggregations,
    ) -> None:
        self.table = table
        self.on = on
        self.join_with = join_with
        self.interval = interval
        self.aggregations = aggregations

    def compile(self) -> tuple[r.RayObject, ...]:  # type: ignore[override]
        agg_dict: dict[str, t.Any] = {}
        for name, expr in self.aggregations.items():
            if isinstance(expr, Expression):
                agg_dict[name] = expr.compile()
            elif isinstance(expr, Column):
                agg_dict[name] = expr.name
            else:
                agg_dict[name] = expr

        return (
            Vector(items=self.on, ray_type=Symbol).ptr,
            self.interval.compile(),
            self.table.ptr,
            *[t.ptr for t in self.join_with],
            Dict(agg_dict).ptr,
        )


class InnerJoin(_Join):
    type_ = Operation.INNER_JOIN


class LeftJoin(_Join):
    type_ = Operation.LEFT_JOIN


class AsofJoin(_Join):
    type_ = Operation.ASOF_JOIN


class WindowJoin(_WindowJoin):
    type_ = Operation.WINDOW_JOIN


class WindowJoin1(_WindowJoin):
    type_ = Operation.WINDOW_JOIN1


class SelectQuery(IPCQueryMixin):
    def __init__(
        self,
        table: _TableProtocol,
        select_cols: tuple[t.Any, t.Any] | None = None,
        where_conditions: list[Expression] | None = None,
        by_cols: tuple[tuple[t.Any, ...], dict[str, t.Any]] | None = None,
        order_by_cols: tuple[tuple[str, ...], bool] | None = None,
    ) -> None:
        self.table = table
        self._select_cols = select_cols
        self._where_conditions = where_conditions or []
        self._by_cols: tuple[tuple[t.Any, ...], dict[str, t.Any]] = (
            by_cols if by_cols is not None else ((), {})
        )
        self._order_by_cols = order_by_cols
        self._ptr: r.RayObject | None = None

    def select(self, *cols, **computed_cols) -> SelectQuery:
        return SelectQuery(
            table=self.table,
            select_cols=(cols, computed_cols),
            where_conditions=self._where_conditions,
            by_cols=self._by_cols,
            order_by_cols=self._order_by_cols,
        )

    def where(self, condition: Expression) -> SelectQuery:
        new_conditions = self._where_conditions.copy()
        new_conditions.append(condition)
        return SelectQuery(
            table=self.table,
            select_cols=self._select_cols,
            where_conditions=new_conditions,
            by_cols=self._by_cols,
            order_by_cols=self._order_by_cols,
        )

    def by(self, *cols, **computed_cols) -> SelectQuery:
        return SelectQuery(
            table=self.table,
            select_cols=self._select_cols,
            where_conditions=self._where_conditions,
            by_cols=(cols, computed_cols),
            order_by_cols=self._order_by_cols,
        )

    def order_by(self, *cols: Column | str, desc: bool = False) -> SelectQuery:
        return SelectQuery(
            table=self.table,
            select_cols=self._select_cols,
            where_conditions=self._where_conditions,
            by_cols=self._by_cols,
            order_by_cols=(tuple(c.name if isinstance(c, Column) else c for c in cols), desc),
        )

    @property
    def ptr(self) -> r.RayObject:
        if self._ptr is None:
            self._ptr = self.compile()
        return self._ptr

    def compile(self) -> r.RayObject:
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

    @property
    def ipc(self) -> r.RayObject:  # type: ignore[override]
        return Expression(Operation.SELECT, self.compile()).compile()

    def execute(self) -> Table:
        if self._order_by_cols:
            cols, desc = self._order_by_cols
            return utils.eval_obj(
                List(
                    [
                        Operation.XDESC if desc else Operation.XASC,
                        List([Operation.SELECT, self.compile()]),
                        Vector(list(cols), ray_type=Symbol),
                    ]
                )
            )

        return utils.eval_obj(List([Operation.SELECT, self.compile()]))


class UpdateQuery(IPCQueryMixin):
    def __init__(
        self, table: _TableProtocol, where_condition: Expression | None = None, **attributes
    ):
        self.table = table
        self.attributes = attributes
        self.where_condition = where_condition

    def where(self, condition: Expression) -> UpdateQuery:
        return UpdateQuery(self.table, where_condition=condition, **self.attributes)

    def compile(self, *, ipc: bool = False) -> r.RayObject:
        where_expr = None
        if self.where_condition:
            if isinstance(self.where_condition, Expression):
                where_expr = self.where_condition.compile(ipc=ipc)
            else:
                where_expr = self.where_condition

        converted_attrs: dict[str, t.Any] = {}
        for key, value in self.attributes.items():
            if isinstance(value, Expression):
                converted_attrs[key] = value.compile(ipc=ipc)
            elif isinstance(value, Column):
                converted_attrs[key] = value.name
            elif isinstance(value, str):
                converted_attrs[key] = (
                    QuotedSymbol(value).ptr
                    if not ipc
                    else Expression(Operation.QUOTE, value).compile()
                )
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

        return Dict(query_items).ptr

    @property
    def ipc(self) -> r.RayObject:  # type: ignore[override]
        return Expression(Operation.UPDATE, self.compile(ipc=True)).compile()

    def execute(self) -> Table:
        new_table = FFI.update(query=self.compile())
        if self.table.is_reference:
            return Table(Symbol(ptr=new_table).value)
        return Table(new_table)


class InsertQuery(IPCQueryMixin):
    def __init__(self, table: _TableProtocol, *args, **kwargs):
        self.table = table
        self.args = args
        self.kwargs = kwargs

        if args and kwargs:
            raise errors.RayforceInitError("Insert query accepts args OR kwargs, not both")

    def compile(self, *, ipc: bool = False) -> r.RayObject:
        if self.args:
            first = self.args[0]

            if isinstance(first, Iterable) and not isinstance(first, (str, bytes)):
                _args = List([]) if not ipc else List([Operation.LIST])
                for sub in self.args:
                    _args.append(
                        Vector(
                            items=sub,
                            ray_type=FFI.get_obj_type(utils.python_to_ray(sub[0])),
                        )
                    )
                insertable = _args.ptr

            else:
                insertable = (
                    List(self.args).ptr if not ipc else List([Operation.LIST, *self.args]).ptr
                )

        elif self.kwargs:
            values = list(self.kwargs.values())
            first_val = values[0]

            if isinstance(first_val, Iterable) and not isinstance(first_val, (str, bytes)):
                keys = Vector(items=list(self.kwargs.keys()), ray_type=Symbol)
                _values = List([])

                for val in values:
                    _values.append(
                        Vector(
                            items=val,
                            ray_type=FFI.get_obj_type(utils.python_to_ray(val[0])),
                        )
                    )
                insertable = Dict.from_items(keys=keys, values=_values).ptr

            else:
                insertable = Dict(self.kwargs).ptr
        else:
            raise errors.RayforceQueryCompilationError("No data to insert")

        return insertable

    @property
    def ipc(self) -> r.RayObject:  # type: ignore[override]
        return Expression(Operation.INSERT, self.table, self.compile(ipc=True)).compile()

    def execute(self) -> Table:
        new_table = FFI.insert(table=FFI.quote(self.table.ptr), data=self.compile())
        if self.table.is_reference:
            return Table(Symbol(ptr=new_table).value)
        return Table(new_table)


class UpsertQuery(IPCQueryMixin):
    def __init__(self, table: _TableProtocol, *args, key_columns: int, **kwargs) -> None:
        self.table = table
        self.args = args
        self.kwargs = kwargs

        if args and kwargs:
            raise errors.RayforceInitError("Upsert query accepts args OR kwargs, not both")

        if key_columns <= 0:
            raise errors.RayforceInitError("key_columns must be greater than 0")
        self.key_columns = key_columns

    def compile(self, *, ipc: bool = False) -> tuple[r.RayObject, r.RayObject]:
        if self.args:
            first = self.args[0]

            if isinstance(first, Iterable) and not isinstance(first, (str, bytes)):
                _args = List([]) if not ipc else List([Operation.LIST])
                for sub in self.args:
                    _args.append(
                        Vector(
                            items=sub,
                            ray_type=FFI.get_obj_type(utils.python_to_ray(sub[0])),
                        )
                    )
                upsertable = _args.ptr

            else:
                _args = List([]) if not ipc else List([Operation.LIST])
                for sub in self.args:
                    _args.append(
                        Vector(
                            items=[sub],
                            ray_type=FFI.get_obj_type(utils.python_to_ray(sub)),
                        )
                    )
                upsertable = _args.ptr

        # TODO: for consistency with insert, allow to use single values isntead of vectors
        elif self.kwargs:
            values = list(self.kwargs.values())
            first_val = values[0]

            if isinstance(first_val, Iterable) and not isinstance(first_val, (str, bytes)):
                keys = Vector(items=list(self.kwargs.keys()), ray_type=Symbol)
                _values = List([])

                for val in values:
                    _values.append(
                        Vector(
                            items=val,
                            ray_type=FFI.get_obj_type(utils.python_to_ray(val[0])),
                        )
                    )
                upsertable = Dict.from_items(keys=keys, values=_values).ptr

            else:
                keys = Vector(items=list(self.kwargs.keys()), ray_type=Symbol)
                _values = List([])

                for val in values:
                    _values.append(
                        Vector(
                            items=[val],
                            ray_type=FFI.get_obj_type(utils.python_to_ray(val)),
                        )
                    )
                upsertable = Dict.from_items(keys=keys, values=_values).ptr
        else:
            raise errors.RayforceQueryCompilationError("No data to insert")

        return I64(self.key_columns).ptr, upsertable

    @property
    def ipc(self) -> r.RayObject:  # type: ignore[override]
        return Expression(Operation.UPSERT, self.table, *self.compile(ipc=True)).compile()

    def execute(self) -> Table:
        compiled = self.compile()
        new_table = FFI.upsert(table=FFI.quote(self.table.ptr), keys=compiled[0], data=compiled[1])
        if self.table.is_reference:
            return Table(Symbol(ptr=new_table).value)
        return Table(new_table)


class PivotQuery:
    AGGFUNC_MAP: t.ClassVar[dict[str, Operation]] = {
        "sum": Operation.SUM,
        "count": Operation.COUNT,
        "avg": Operation.AVG,
        "min": Operation.MIN,
        "max": Operation.MAX,
        "first": Operation.FIRST,
        "last": Operation.LAST,
    }

    def __init__(
        self,
        table: _TableProtocol,
        index: str | list[str],
        columns: str,
        values: str,
        aggfunc: str = "min",
    ) -> None:
        if aggfunc not in self.AGGFUNC_MAP:
            raise errors.RayforceValueError(
                f"Invalid aggfunc '{aggfunc}'. Must be one of: {list(self.AGGFUNC_MAP.keys())}"
            )
        self.table = t.cast("Table", table)
        self.index = [index] if isinstance(index, str) else list(index)
        self.columns = columns
        self.values = values
        self.aggfunc = aggfunc

    def execute(self) -> Table:
        distinct = self.table.select(_col=Column(self.columns).distinct()).execute()
        unique_values = [v.value if hasattr(v, "value") else v for v in distinct["_col"]]
        if not unique_values:
            raise errors.RayforceValueError(f"No values in pivot column '{self.columns}'")

        tables: list[Table] = []
        for val in unique_values:
            filtered = (
                self.table.select(*self.index, self.values)
                .where(Column(self.columns) == val)
                .execute()
            )
            tables.append(
                filtered.select(
                    **{str(val): Expression(self.AGGFUNC_MAP[self.aggfunc], Column(self.values))}
                )
                .by(*self.index)
                .execute()
            )

        result = tables[0]
        for tbl in tables[1:]:
            result = result.left_join(tbl, on=self.index).execute()

        return result


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

    def compile(self) -> r.RayObject:
        return List(
            [
                Operation.MAP_LEFT,
                Operation.ADD,
                Vector([self.lower, self.upper], ray_type=I64),
                List(
                    [
                        Operation.AT,
                        self.table.ptr,
                        List(
                            [
                                Operation.QUOTE,
                                self.column.name
                                if isinstance(self.column, Column)
                                else self.column,
                            ]
                        ),
                    ]
                ),
            ]
        ).ptr


__all__ = [
    "AsofJoin",
    "Column",
    "Expression",
    "InnerJoin",
    "InsertQuery",
    "LeftJoin",
    "PivotQuery",
    "Table",
    "TableColumnInterval",
    "UpdateQuery",
    "UpsertQuery",
    "WindowJoin",
    "WindowJoin1",
]

TypeRegistry.register(type_code=r.TYPE_TABLE, type_class=Table)
