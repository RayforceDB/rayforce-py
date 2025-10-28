from __future__ import annotations
from typing import Any, Callable, Union, List, Dict, Tuple, Optional

from raypy import _rayforce as r
from raypy import api
from raypy.types import queries as q
from raypy.types import primitive as p
from raypy.types import container as c
from raypy.types import scalar as s
from raypy.queries import select as legacy_select
from raypy.queries import update as legacy_update
from raypy.queries import insert as legacy_insert
from raypy.queries import upsert as legacy_upsert
from raypy.queries import inner_join as legacy_inner_join
from raypy.queries import window_join as legacy_window_join
from raypy import misc


class Expression:
    
    def __init__(self, operation: p.Operation, *operands):
        self.operation = operation
        self.operands = operands
    
    def to_legacy(self) -> q.Expression:
        converted_operands = []

        for idx, operand in enumerate(self.operands):
            if isinstance(operand, Expression):
                converted_operands.append(operand.to_legacy())
            elif isinstance(operand, Column):
                converted_operands.append(operand.name)
            elif isinstance(operand, FilteredColumn):
                converted_operands.append(self._build_filtered_column(operand))
            elif hasattr(operand, 'ptr'):
                converted_operands.append(operand)
            elif isinstance(operand, str):
                if self.operation == p.Operation.AT and idx == 1:
                    converted_operands.append(operand)
                else:
                    converted_operands.append(s.QuotedSymbol(operand))
            else:
                converted_operands.append(operand)
        
        return q.Expression(self.operation, *converted_operands)

    def _build_filtered_column(self, filtered_col: FilteredColumn) -> q.Expression:
        if isinstance(filtered_col.condition, Expression):
            where_expr = filtered_col.condition.to_legacy()
        elif isinstance(filtered_col.condition, Column):
            where_expr = filtered_col.condition.name
        else:
            where_expr = filtered_col.condition
            
        where_wrapped = q.Expression(p.Operation.WHERE, where_expr)
        
        return q.Expression(
            p.Operation.MAP,
            p.Operation.AT,
            filtered_col.column.name,
            where_wrapped
        )
    
    def count(self) -> Expression:
        return Expression(p.Operation.COUNT, self)
    
    def sum(self) -> Expression:
        return Expression(p.Operation.SUM, self)
    
    def mean(self) -> Expression:
        return Expression(p.Operation.AVG, self)
    
    def avg(self) -> Expression:
        return Expression(p.Operation.AVG, self)
    
    def __and__(self, other) -> Expression:
        return Expression(p.Operation.AND, self, other)
    
    def __or__(self, other) -> Expression:
        return Expression(p.Operation.OR, self, other)
    
    def __add__(self, other) -> Expression:
        return Expression(p.Operation.ADD, self, other)
    
    def __sub__(self, other) -> Expression:
        return Expression(p.Operation.SUBSTRACT, self, other)
    
    def __mul__(self, other) -> Expression:
        return Expression(p.Operation.MULTIPLY, self, other)
    
    def __truediv__(self, other) -> Expression:
        return Expression(p.Operation.DIVIDE, self, other)
    
    def __mod__(self, other) -> Expression:
        return Expression(p.Operation.MODULO, self, other)
    
    def __eq__(self, other) -> Expression:
        return Expression(p.Operation.EQUALS, self, other)
    
    def __ne__(self, other) -> Expression:
        return Expression(p.Operation.NOT_EQUALS, self, other)
    
    def __lt__(self, other) -> Expression:
        return Expression(p.Operation.LE, self, other)
    
    def __le__(self, other) -> Expression:
        return Expression(p.Operation.LTE, self, other)
    
    def __gt__(self, other) -> Expression:
        return Expression(p.Operation.GE, self, other)
    
    def __ge__(self, other) -> Expression:
        return Expression(p.Operation.GTE, self, other)
    
    def __repr__(self) -> str:
        return f"Expression({self.operation.value}, {len(self.operands)} operands)"


class Column:
    
    def __init__(self, name: str, table: Optional[Table] = None):
        self.name = name
        self.table = table
    
    def __eq__(self, other) -> Expression:
        return Expression(p.Operation.EQUALS, self, other)
    
    def __ne__(self, other) -> Expression:
        return Expression(p.Operation.NOT_EQUALS, self, other)
    
    def __lt__(self, other) -> Expression:
        return Expression(p.Operation.LE, self, other)
    
    def __le__(self, other) -> Expression:
        return Expression(p.Operation.LTE, self, other)
    
    def __gt__(self, other) -> Expression:
        return Expression(p.Operation.GE, self, other)
    
    def __ge__(self, other) -> Expression:
        return Expression(p.Operation.GTE, self, other)
    
    def __add__(self, other) -> Expression:
        return Expression(p.Operation.ADD, self, other)
    
    def __sub__(self, other) -> Expression:
        return Expression(p.Operation.SUBSTRACT, self, other)
    
    def __mul__(self, other) -> Expression:
        return Expression(p.Operation.MULTIPLY, self, other)
    
    def __truediv__(self, other) -> Expression:
        return Expression(p.Operation.DIVIDE, self, other)
    
    def __mod__(self, other) -> Expression:
        return Expression(p.Operation.MODULO, self, other)
    
    def __radd__(self, other) -> Expression:
        return Expression(p.Operation.ADD, other, self)
    
    def __rsub__(self, other) -> Expression:
        return Expression(p.Operation.SUBSTRACT, other, self)
    
    def __rmul__(self, other) -> Expression:
        return Expression(p.Operation.MULTIPLY, other, self)
    
    def __rtruediv__(self, other) -> Expression:
        return Expression(p.Operation.DIVIDE, other, self)
    
    def __and__(self, other) -> Expression:
        return Expression(p.Operation.AND, self, other)
    
    def __or__(self, other) -> Expression:
        return Expression(p.Operation.OR, self, other)
    
    def sum(self) -> Expression:
        return Expression(p.Operation.SUM, self)
    
    def mean(self) -> Expression:
        return Expression(p.Operation.AVG, self)
    
    def avg(self) -> Expression:
        return Expression(p.Operation.AVG, self)
    
    def max(self) -> Expression:
        return Expression(p.Operation.MAX, self)
    
    def min(self) -> Expression:
        return Expression(p.Operation.MIN, self)
    
    def count(self) -> Expression:
        return Expression(p.Operation.COUNT, self)
    
    def first(self) -> Expression:
        return Expression(p.Operation.FIRST, self)
    
    def last(self) -> Expression:
        return Expression(p.Operation.LAST, self)
    
    def median(self) -> Expression:
        return Expression(p.Operation.MEDIAN, self)
    
    def distinct(self) -> Expression:
        return Expression(p.Operation.DISTINCT, self)

    def isin(self, values: List) -> Expression:
        if values and isinstance(values[0], str):
            quoted_items = [s.QuotedSymbol(v) for v in values]
            vec = c.Vector(type_code=s.Symbol.type_code, items=quoted_items)
        else:
            vec = c.List(values)
        
        return Expression(p.Operation.IN, self, vec)

    def where(self, condition: Expression) -> FilteredColumn:
        return FilteredColumn(self, condition)
    
    def __getitem__(self, condition: Expression) -> FilteredColumn:
        return self.where(condition)
    
    def asc(self) -> SortColumn:
        return SortColumn(self, ascending=True)
    
    def desc(self) -> SortColumn:
        return SortColumn(self, ascending=False)
    
    def __repr__(self) -> str:
        return f"Column('{self.name}')"


class DictLookup(Expression):
    def __init__(self, dict_obj, key: Union[Column, str]):
        self.dict_obj = dict_obj
        self.key = key.name if isinstance(key, Column) else key
        super().__init__(p.Operation.AT, dict_obj, self.key)


class FilteredColumn:
    
    def __init__(self, column: Column, condition: Expression):
        self.column = column
        self.condition = condition
    
    def sum(self) -> Expression:
        return Expression(p.Operation.SUM, self)
    
    def mean(self) -> Expression:
        return Expression(p.Operation.AVG, self)
    
    def avg(self) -> Expression:
        return Expression(p.Operation.AVG, self)
    
    def max(self) -> Expression:
        return Expression(p.Operation.MAX, self)
    
    def min(self) -> Expression:
        return Expression(p.Operation.MIN, self)
    
    def count(self) -> Expression:
        return Expression(p.Operation.COUNT, self)
    
    def __repr__(self) -> str:
        return f"FilteredColumn({self.column.name} where ...)"


class SortColumn:
    
    def __init__(self, column: Column, ascending: bool = True):
        self.column = column
        self.ascending = ascending
    
    def __repr__(self) -> str:
        direction = "asc" if self.ascending else "desc"
        return f"{self.column.name} {direction}"


class GroupByBuilder:
    
    def __init__(self, table: Union[str, c.Table], group_cols: List[str]):
        self._table = table
        self._group_cols = group_cols
    
    def agg(self, **aggregations) -> Table:
        attributes = {}
        
        attributes["by"] = {col: col for col in self._group_cols}
        
        for name, expr in aggregations.items():
            if isinstance(expr, Expression):
                attributes[name] = expr.to_legacy()
            elif isinstance(expr, Column):
                attributes[name] = expr.name
            else:
                attributes[name] = expr
        
        query = q.SelectQuery(
            select_from=self._table,
            attributes=attributes
        )
        
        result = legacy_select(query)
        return Table(ptr=result.ptr)
    
    def __repr__(self) -> str:
        return f"GroupByBuilder(group_by={self._group_cols})"


class QueryBuilder:
    
    def __init__(
        self,
        table: Union[str, c.Table],
        select_cols: Optional[Tuple] = None,
        where_conditions: Optional[List[Expression]] = None,
        order_by_cols: Optional[List[SortColumn]] = None,
        limit: Optional[int] = None
    ):
        self._table = table
        self._select_cols = select_cols
        self._where_conditions = where_conditions or []
        self._order_by_cols = order_by_cols or []
        self._limit = limit
    
    def select(self, *cols, **computed_cols) -> QueryBuilder:
        return QueryBuilder(
            table=self._table,
            select_cols=(cols, computed_cols),
            where_conditions=self._where_conditions,
            order_by_cols=self._order_by_cols,
            limit=self._limit
        )
    
    def where(self, condition: Union[Expression, Callable]) -> QueryBuilder:
        if callable(condition):
            temp_table = Table._create_proxy(self._table)
            condition = condition(temp_table)
        
        new_conditions = self._where_conditions.copy()
        new_conditions.append(condition)
        
        return QueryBuilder(
            table=self._table,
            select_cols=self._select_cols,
            where_conditions=new_conditions,
            order_by_cols=self._order_by_cols,
            limit=self._limit
        )
    
    def order_by(self, *cols, ascending: bool = True) -> QueryBuilder:
        sort_cols = []
        for col in cols:
            if isinstance(col, str):
                sort_cols.append(SortColumn(Column(col), ascending=ascending))
            elif isinstance(col, Column):
                sort_cols.append(SortColumn(col, ascending=ascending))
            elif isinstance(col, SortColumn):
                sort_cols.append(col)
        
        return QueryBuilder(
            table=self._table,
            select_cols=self._select_cols,
            where_conditions=self._where_conditions,
            order_by_cols=self._order_by_cols + sort_cols,
            limit=self._limit
        )
    
    def limit(self, n: int) -> QueryBuilder:
        return QueryBuilder(
            table=self._table,
            select_cols=self._select_cols,
            where_conditions=self._where_conditions,
            order_by_cols=self._order_by_cols,
            limit=n
        )
    
    def execute(self) -> Table:
        query = self._build_legacy_query()
        result = legacy_select(query)
        return Table(ptr=result.ptr)
    
    def _build_legacy_query(self) -> q.SelectQuery:
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
                    attributes[name] = expr.to_legacy()
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
            where_expr = combined.to_legacy()
        
        return q.SelectQuery(
            select_from=self._table,
            attributes=attributes,
            where=where_expr
        )
    
    def _convert_expr(self, expr: Union[Expression, Column]) -> Union[q.Expression, str]:
        if isinstance(expr, Expression):
            return expr.to_legacy()
        elif isinstance(expr, Column):
            return expr.name
        return expr
    
    def __iter__(self):
        result = self.execute()
        return iter(result.values().value)
    
    def __repr__(self) -> str:
        parts = [f"QueryBuilder(table={self._table}"]
        if self._select_cols:
            parts.append(f", select=...")
        if self._where_conditions:
            parts.append(f", where={len(self._where_conditions)} conditions")
        return "".join(parts) + ")"


class Table:
    
    def __init__(
        self,
        name_or_data: Union[str, None] = None,
        columns: Optional[List[str]] = None,
        values: Optional[List] = None,
        ptr = None
    ):
        if isinstance(name_or_data, str):
            self._table = name_or_data
            self._is_ref = True
        elif ptr is not None:
            self._table = c.Table(ptr=ptr)
            self._is_ref = False
        elif columns and values:
            self._table = c.Table(columns=columns, values=values)
            self._is_ref = False
        else:
            raise ValueError("Must provide either name, columns/values, or ptr")

    def __getattr__(self, name: str) -> Column:
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        return Column(name, table=self)

    def select(self, *cols, **computed_cols) -> QueryBuilder:
        builder = QueryBuilder(table=self._table)
        return builder.select(*cols, **computed_cols)
    
    def where(self, condition: Union[Expression, Callable]) -> QueryBuilder:
        builder = QueryBuilder(table=self._table)
        return builder.where(condition)
    
    def order_by(self, *cols, ascending: bool = True) -> QueryBuilder:
        builder = QueryBuilder(table=self._table)
        return builder.order_by(*cols, ascending=ascending)
    
    def limit(self, n: int) -> QueryBuilder:
        builder = QueryBuilder(table=self._table)
        return builder.limit(n)
    
    def group_by(self, *cols) -> GroupByBuilder:
        return GroupByBuilder(table=self._table, group_cols=list(cols))
    
    def concat(self, *others: Table) -> Table:
        result = self._table
        for other in others:
            other_table = other._table if isinstance(other, Table) else other
            expr = Expression(p.Operation.CONCAT, result, other_table)
            result = misc.eval_obj(expr.to_legacy())
        return Table(ptr=result.ptr)
    
    @staticmethod
    def concat_all(tables: List[Table]) -> Table:
        if not tables:
            raise ValueError("Must provide at least one table")
        return tables[0].concat(*tables[1:])
    
    def join(
        self,
        other: Table,
        on: Union[str, List[str]],
        how: str = "inner"
    ) -> Table:
        if isinstance(on, str):
            on = [on]
        
        join_keys = c.Vector(type_code=s.Symbol.type_code, items=on)
        
        if how == "inner":
            other_table = other._table if isinstance(other, Table) else other
            self_table = self._table
            result = legacy_inner_join(
                join_by=join_keys,
                to_join=[self_table, other_table]
            )
        else:
            raise ValueError(f"Join type '{how}' not yet supported. Use 'inner'.")
        
        return Table(ptr=result.ptr)
    
    def inner_join(self, other: Table, on: Union[str, List[str]]) -> Table:
        return self.join(other, on=on, how="inner")
    
    def window_join(
        self,
        other: Table,
        on: Union[str, List[str]],
        by: Optional[Union[str, List[str]]] = None
    ) -> Table:
        if isinstance(on, str):
            on = [on]
        if by and isinstance(by, str):
            by = [by]
        
        join_keys = c.Vector(type_code=s.Symbol.type_code, items=on)
        
        other_table = other._table if isinstance(other, Table) else other
        self_table = self._table
        result = legacy_window_join(
            join_by=join_keys,
            to_join=[self_table, other_table]
        )
        
        return Table(ptr=result.ptr)
    
    def update(self, **kwargs) -> UpdateQuery:
        return UpdateQuery(self._table, **kwargs)
    
    def insert(self, *args, **kwargs) -> InsertQuery:
        return InsertQuery(self._table, *args, **kwargs)
    
    def upsert(
        self,
        data: Union[Dict, List[Dict]],
        match_on: Union[str, List[str]] = "id"
    ) -> UpsertQuery:
        return UpsertQuery(self._table, data, match_on)

    def head(self, n: int = 5) -> Table:
        return self.limit(n).execute()
    
    def show(self, n: int = 20) -> None:
        if n:
            result = self.head(n)
        else:
            result = self._get_table()
        print(result)
    
    def save(self, name: str) -> None:
        misc.set_table_name(table=self._table, name=name)
    
    def _get_table(self) -> c.Table:
        if self._is_ref:
            return misc.eval_str(self._table)
        return self._table
    
    @property
    def columns(self) -> List[str]:
        if isinstance(self._table, c.Table):
            cols = self._table.columns()
            return [col.value for col in cols]
        return []
    
    def values(self):
        if isinstance(self._table, c.Table):
            return self._table.values()
        return None
    
    @property
    def shape(self) -> Tuple[int, int]:
        if isinstance(self._table, c.Table):
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
    def from_dict(cls, data: Dict[str, List]) -> Table:
        columns = list(data.keys())
        values = list(data.values())
        return cls(columns=columns, values=values)
    
    @classmethod
    def from_records(cls, records: List[Dict]) -> Table:
        if not records:
            raise ValueError("Cannot create table from empty records")
        
        columns = list(records[0].keys())
        values = {col: [] for col in columns}
        
        for record in records:
            for col in columns:
                values[col].append(record.get(col))
        
        return cls.from_dict(values)
    
    @classmethod
    def get(cls, name: str) -> Table:
        return cls(name)
    
    @staticmethod
    def _create_proxy(table: Union[str, c.Table]) -> Table:
        proxy = object.__new__(Table)
        proxy._table = table
        proxy._is_ref = isinstance(table, str)
        return proxy
    
    def __str__(self) -> str:
        if isinstance(self._table, c.Table):
            return api.repr_table(self._table.ptr)
        elif isinstance(self._table, str):
            table = misc.eval_str(self._table)
            return api.repr_table(table.ptr)
        return f"Table('{self._table}')"
    
    def __repr__(self) -> str:
        if self._is_ref:
            return f"Table('{self._table}')"
        return f"Table(columns={self.columns})"


class UpdateQuery:
    def __init__(self, table: Union[str, c.Table], **attributes):
        self._table = table
        self._attributes = attributes
        self._where_condition = None
    
    def where(self, condition: Union[Expression, Callable]) -> UpdateQuery:
        if callable(condition):
            temp = Table._create_proxy(self._table)
            condition = condition(temp)
        self._where_condition = condition
        return self
    
    def execute(self) -> Union[Table, bool]:
        where_expr = None
        if self._where_condition:
            if isinstance(self._where_condition, Expression):
                where_expr = self._where_condition.to_legacy()
            else:
                where_expr = self._where_condition
        
        converted_attrs = {}
        for key, value in self._attributes.items():
            if isinstance(value, Expression):
                converted_attrs[key] = value.to_legacy()
            elif isinstance(value, Column):
                converted_attrs[key] = value.name
            elif isinstance(value, DictLookup):
                converted_attrs[key] = value.to_legacy()
            else:
                converted_attrs[key] = value
        
        query = q.UpdateQuery(
            update_from=self._table,
            attributes=converted_attrs,
            where=where_expr
        )
        result = legacy_update(query)
        
        if isinstance(result, bool):
            return result
        return Table(ptr=result.ptr)
    
    def __repr__(self) -> str:
        return f"UpdateQuery(set={list(self._attributes.keys())}, where={self._where_condition is not None})"


class InsertQuery:
    def __init__(self, table: Union[str, c.Table], *args, **kwargs):
        self._table = table
        
        if args:
            self._insertable = args[0] if len(args) == 1 else list(args)
        elif kwargs:
            self._insertable = list(kwargs.values())
        else:
            raise ValueError("No data to insert")
    
    def execute(self) -> Table:
        query = q.InsertQuery(insert_to=self._table, insertable=self._insertable)
        result = legacy_insert(query.insert_to_ptr, query.insertable_ptr)
        return Table(ptr=result.ptr)
    
    def __repr__(self) -> str:
        return f"InsertQuery({len(self._insertable)} values)"


class UpsertQuery:
    
    def __init__(
        self,
        table: Union[str, c.Table],
        data: Union[Dict, List[Dict]],
        match_on: Union[str, List[str]]
    ):
        self._table = table
        self._data = data if isinstance(data, list) else [data]
        self._match_by_first = 1 if isinstance(match_on, str) else len(match_on)
    
    def execute(self) -> Table:
        upsertable = {}
        for row in self._data:
            for key, value in row.items():
                if key not in upsertable:
                    upsertable[key] = []
                upsertable[key].append(value)
        
        query = q.UpsertQuery(
            upsert_to=self._table,
            match_by_first=self._match_by_first,
            upsertable=upsertable
        )
        result = legacy_upsert(query.upsert_to_ptr, query.match_ptr, query.upsertable_ptr)
        return Table(ptr=result.ptr)
    
    def __repr__(self) -> str:
        return f"UpsertQuery({len(self._data)} rows, match_by_first={self._match_by_first})"


def lookup(dict_obj, column: Union[Column, str]) -> DictLookup:
    return DictLookup(dict_obj, column)


__all__ = [
    'Table',
    'Column',
    'Expression',
    'FilteredColumn',
    'SortColumn',
    'QueryBuilder',
    'GroupByBuilder',
    'UpdateQuery',
    'InsertQuery',
    'UpsertQuery',
    'DictLookup',
    'lookup',
]
