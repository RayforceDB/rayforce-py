from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import typing as t

if t.TYPE_CHECKING:
    import sqlglot.expressions as exp  # type: ignore[import-not-found]

    from rayforce.types.table import Table


def _ensure_sqlglot():
    try:
        import sqlglot
    except ImportError as e:
        raise ImportError(
            "sqlglot is required for SQL support. Install it with: pip install rayforce-py[sql]"
        ) from e
    return sqlglot


OP_MAP = {
    "=": "__eq__",
    "!=": "__ne__",
    ">": "__gt__",
    ">=": "__ge__",
    "<": "__lt__",
    "<=": "__le__",
    "+": "__add__",
    "-": "__sub__",
    "*": "__mul__",
    "/": "__truediv__",
    "%": "__mod__",
    "AND": "__and__",
    "OR": "__or__",
}

FUNC_MAP = {
    "COUNT": "count",
    "SUM": "sum",
    "AVG": "avg",
    "MIN": "min",
    "MAX": "max",
    "FIRST": "first",
    "LAST": "last",
    "MEDIAN": "median",
    "DISTINCT": "distinct",
}


class ExprType(Enum):
    COLUMN = "column"
    LITERAL = "literal"
    BINARY_OP = "binary_op"
    UNARY_OP = "unary_op"
    FUNCTION = "function"
    IN_LIST = "in_list"
    STAR = "star"


@dataclass
class ParsedExpr:
    type: ExprType
    value: t.Any = None
    op: str | None = None
    left: ParsedExpr | None = None
    right: ParsedExpr | None = None
    args: list[ParsedExpr] = field(default_factory=list)


@dataclass
class ParsedSelect:
    columns: list[tuple[str | None, ParsedExpr]]  # (alias, expr)
    where_clause: ParsedExpr | None = None
    group_by: list[str] = field(default_factory=list)
    order_by: list[tuple[str, bool]] = field(default_factory=list)  # (col, is_desc)


@dataclass
class ParsedUpdate:
    assignments: dict[str, ParsedExpr]
    where_clause: ParsedExpr | None = None


@dataclass
class ParsedInsert:
    columns: list[str] | None
    values: list[list[ParsedExpr]]


@dataclass
class ParsedUpsert:
    columns: list[str] | None
    values: list[list[ParsedExpr]]
    key_columns: int


ParsedQuery = ParsedSelect | ParsedUpdate | ParsedInsert | ParsedUpsert


class SQLParser:
    def parse(self, sql: str) -> ParsedQuery:
        ast = _ensure_sqlglot().parse_one(sql)

        if ast.key == "select":
            return self._parse_select(ast)
        if ast.key == "update":
            return self._parse_update(ast)
        if ast.key == "insert":
            if ast.args.get("conflict"):  # upsert
                return self._parse_upsert(ast)
            return self._parse_insert(ast)
        raise ValueError(f"Statement not supported: {ast.key}")

    def _parse_select(self, node: exp.Select) -> ParsedSelect:
        import sqlglot.expressions as exp

        columns: list[tuple[str | None, ParsedExpr]] = []
        for expr in node.expressions:
            alias = None
            if isinstance(expr, exp.Alias):
                alias = expr.alias
                expr = expr.this  # noqa: PLW2901
            columns.append((alias, self._parse_expr(expr)))

        where_clause = None
        if _where := node.args.get("where"):
            where_clause = self._parse_expr(_where.this)

        group_by: list[str] = []
        if _group := node.args.get("group"):
            group_by = [g.name if isinstance(g, exp.Column) else str(g) for g in _group]

        order_by: list[tuple[str, bool]] = []
        if _order := node.args.get("order"):
            for o in _order.expressions:
                is_desc = isinstance(o, exp.Ordered) and o.args.get("desc", False)
                col_expr = o.this if isinstance(o, exp.Ordered) else o
                if isinstance(col_expr, exp.Column):
                    order_by.append((col_expr.name, is_desc))
                else:
                    order_by.append((str(col_expr), is_desc))

        return ParsedSelect(
            columns=columns, where_clause=where_clause, group_by=group_by, order_by=order_by
        )

    def _parse_update(self, node: exp.Expression) -> ParsedUpdate:
        import sqlglot.expressions as exp

        assignments: dict[str, ParsedExpr] = {}
        for expr in node.expressions:
            if isinstance(expr, exp.EQ):
                col_name = expr.this.name if isinstance(expr.this, exp.Column) else str(expr.this)
                assignments[col_name] = self._parse_expr(expr.expression)

        where_clause = None
        if _where := node.args.get("where"):
            where_clause = self._parse_expr(_where.this)

        return ParsedUpdate(assignments=assignments, where_clause=where_clause)

    def __parse_upinsert(
        self, node: exp.Expression
    ) -> tuple[list[str] | None, list[list[ParsedExpr]]]:
        import sqlglot.expressions as exp

        columns: list[str] | None = None
        if hasattr(node.this, "expressions") and (_expressions := node.this.expressions):
            columns = [c.name if isinstance(c, exp.Column) else str(c) for c in _expressions]

        values: list[list[ParsedExpr]] = []
        if (_values_clause := node.args.get("expression")) and hasattr(
            _values_clause, "expressions"
        ):
            for row_tuple in _values_clause.expressions:
                if hasattr(row_tuple, "expressions"):
                    row = [self._parse_expr(val) for val in row_tuple.expressions]
                    values.append(row)

        if not values:
            raise ValueError("Statement must have VALUES")

        return columns, values

    def _parse_insert(self, node: exp.Expression) -> ParsedInsert:
        columns, values = self.__parse_upinsert(node)
        return ParsedInsert(columns=columns, values=values)

    def _parse_upsert(self, node: exp.Expression) -> ParsedUpsert:
        columns, values = self.__parse_upinsert(node)

        conflict_keys: list[str] = []
        if _conflict := node.args.get("conflict"):
            if str(_conflict.args.get("action")) == "DO NOTHING":
                raise ValueError("ON CONFLICT DO NOTHING is not supported, use DO UPDATE")

            conflict_keys = [
                k.name if hasattr(k, "name") else str(k)
                for k in _conflict.args.get("conflict_keys", [])
            ]

            if _conflict.args.get("duplicate") and not conflict_keys:
                raise ValueError("ON DUPLICATE KEY UPDATE requires explicit key columns")

        if not conflict_keys:
            raise ValueError("UPSERT requires ON CONFLICT (key_columns) clause")

        if columns:
            for i, key in enumerate(conflict_keys):
                if i >= len(columns) or columns[i] != key:
                    raise ValueError(
                        f"Conflict key '{key}' must match the first {len(conflict_keys)} columns. "
                        f"Expected '{columns[i] if i < len(columns) else 'N/A'}' at position {i}"
                    )

        return ParsedUpsert(columns=columns, values=values, key_columns=len(conflict_keys))

    def _parse_expr(self, node: exp.Expression) -> ParsedExpr:
        import sqlglot.expressions as exp

        if isinstance(node, exp.Column):
            return ParsedExpr(type=ExprType.COLUMN, value=node.name)

        if isinstance(node, exp.Star):
            return ParsedExpr(type=ExprType.STAR)

        if isinstance(node, exp.Literal):
            if node.is_number:
                val = float(node.this) if "." in node.this else int(node.this)
            else:
                val = node.this
            return ParsedExpr(type=ExprType.LITERAL, value=val)

        if isinstance(node, exp.Boolean):
            return ParsedExpr(type=ExprType.LITERAL, value=node.this)

        if isinstance(node, exp.Null):
            return ParsedExpr(type=ExprType.LITERAL, value=None)

        if isinstance(node, exp.Paren):
            return self._parse_expr(node.this)

        if isinstance(node, (exp.EQ, exp.NEQ, exp.GT, exp.GTE, exp.LT, exp.LTE)):
            op_map = {
                exp.EQ: "=",
                exp.NEQ: "!=",
                exp.GT: ">",
                exp.GTE: ">=",
                exp.LT: "<",
                exp.LTE: "<=",
            }
            return ParsedExpr(
                type=ExprType.BINARY_OP,
                op=op_map[type(node)],
                left=self._parse_expr(node.this),
                right=self._parse_expr(node.expression),
            )

        if isinstance(node, exp.And):
            return ParsedExpr(
                type=ExprType.BINARY_OP,
                op="AND",
                left=self._parse_expr(node.this),
                right=self._parse_expr(node.expression),
            )

        if isinstance(node, exp.Or):
            return ParsedExpr(
                type=ExprType.BINARY_OP,
                op="OR",
                left=self._parse_expr(node.this),
                right=self._parse_expr(node.expression),
            )

        if isinstance(node, exp.Not):
            return ParsedExpr(
                type=ExprType.UNARY_OP,
                op="NOT",
                left=self._parse_expr(node.this),
            )

        if isinstance(node, exp.Neg):
            inner = self._parse_expr(node.this)
            if inner.type == ExprType.LITERAL and isinstance(inner.value, (int, float)):
                return ParsedExpr(type=ExprType.LITERAL, value=-inner.value)
            return ParsedExpr(type=ExprType.UNARY_OP, op="NEG", left=inner)

        if isinstance(node, (exp.Add, exp.Sub, exp.Mul, exp.Div, exp.Mod)):
            op_map = {
                exp.Add: "+",
                exp.Sub: "-",
                exp.Mul: "*",
                exp.Div: "/",
                exp.Mod: "%",
            }
            return ParsedExpr(
                type=ExprType.BINARY_OP,
                op=op_map[type(node)],
                left=self._parse_expr(node.this),
                right=self._parse_expr(node.expression),
            )

        if isinstance(node, exp.In):
            return ParsedExpr(
                type=ExprType.IN_LIST,
                left=self._parse_expr(node.this),
                args=[self._parse_expr(v) for v in node.expressions],
            )

        if isinstance(node, exp.Func):
            args: list[ParsedExpr] = []

            if (
                hasattr(node, "this")
                and ((_this := node.this) is not None)
                and isinstance(_this, exp.Expression)
            ):
                args.append(self._parse_expr(_this))

            if hasattr(node, "expressions") and (_expressions := node.expressions):
                args.extend(
                    [
                        self._parse_expr(expr)
                        for expr in _expressions
                        if isinstance(expr, exp.Expression)
                    ]
                )

            return ParsedExpr(type=ExprType.FUNCTION, value=node.key.upper(), args=args)

        raise ValueError(f"Unsupported SQL expression type: {type(node).__name__}")


class SQLCompiler:
    def compile(self, parsed: ParsedQuery, table: Table) -> Table:
        if isinstance(parsed, ParsedSelect):
            return self._compile_select(parsed, table)
        if isinstance(parsed, ParsedUpdate):
            return self._compile_update(parsed, table)
        if isinstance(parsed, ParsedInsert):
            return self._compile_insert(parsed, table)
        if isinstance(parsed, ParsedUpsert):
            return self._compile_upsert(parsed, table)
        raise ValueError(f"Unsupported query type: {type(parsed).__name__}")

    def _compile_select(self, parsed: ParsedSelect, table: Table) -> Table:
        select_args: list[str] = []
        select_kwargs: dict[str, t.Any] = {}

        for alias, expr in parsed.columns:
            if expr.type == ExprType.STAR:
                select_args.append("*")
            elif expr.type == ExprType.COLUMN and alias is None:
                select_args.append(expr.value)
            else:
                name = alias if alias else self._infer_name(expr)
                select_kwargs[name] = self._compile_expr(expr)

        query = (
            table.select(*select_args, **select_kwargs)
            if select_args or select_kwargs
            else table.select("*")
        )

        if _where := parsed.where_clause:
            query = query.where(self._compile_expr(_where))

        if _by := parsed.group_by:
            query = query.by(*_by)

        if _order := parsed.order_by:
            desc = any(is_desc for _, is_desc in parsed.order_by)
            query = query.order_by(*[col for col, _ in _order], desc=desc)

        return query.execute()

    def _compile_update(self, parsed: ParsedUpdate, table: Table) -> Table:
        update_kwargs: dict[str, t.Any] = {
            col_name: self._compile_expr(expr) for col_name, expr in parsed.assignments.items()
        }

        query = table.update(**update_kwargs)
        if _where := parsed.where_clause:
            query = query.where(self._compile_expr(_where))

        return query.execute()

    def _compile_insert(self, parsed: ParsedInsert, table: Table) -> Table:
        compiled_rows: list[list[t.Any]] = [
            [self._compile_expr(val) for val in row] for row in parsed.values
        ]

        if _columns := parsed.columns:
            # INSERT with column names: use kwargs style
            insert_kwargs: dict[str, list[t.Any]] = {col: [] for col in _columns}
            for row in compiled_rows:
                for i, col in enumerate(_columns):
                    insert_kwargs[col].append(row[i])
            return table.insert(**insert_kwargs).execute()

        if len(compiled_rows) == 1:
            return table.insert(*compiled_rows[0]).execute()

        return table.insert(
            *[[row[i] for row in compiled_rows] for i in range(len(compiled_rows[0]))]
        ).execute()

    def _compile_upsert(self, parsed: ParsedUpsert, table: Table) -> Table:
        compiled_rows: list[list[t.Any]] = [
            [self._compile_expr(val) for val in row] for row in parsed.values
        ]

        if parsed.columns:
            upsert_kwargs: dict[str, list[t.Any]] = {col: [] for col in parsed.columns}
            for row in compiled_rows:
                for i, col in enumerate(parsed.columns):
                    upsert_kwargs[col].append(row[i])
            return table.upsert(**upsert_kwargs, key_columns=parsed.key_columns).execute()

        if len(compiled_rows) == 1:
            return table.upsert(*compiled_rows[0], key_columns=parsed.key_columns).execute()

        return table.upsert(
            *[[row[i] for row in compiled_rows] for i in range(len(compiled_rows[0]))],
            key_columns=parsed.key_columns,
        ).execute()

    def _compile_expr(self, expr: ParsedExpr) -> t.Any:
        from rayforce.types.table import Column

        if expr.type == ExprType.COLUMN:
            return Column(expr.value)

        if expr.type == ExprType.LITERAL:
            return expr.value

        if expr.type == ExprType.STAR:
            return "*"

        if expr.type == ExprType.BINARY_OP:
            assert expr.left is not None
            assert expr.right is not None
            assert expr.op is not None
            left, right = self._compile_expr(expr.left), self._compile_expr(expr.right)

            op_method = OP_MAP.get(expr.op)
            if op_method and hasattr(left, op_method):
                return getattr(left, op_method)(right)

            raise ValueError(f"Unsupported binary operator: {expr.op}")

        if expr.type == ExprType.UNARY_OP:
            assert expr.left is not None
            if expr.op == "NOT":
                return self._compile_expr(expr.left).is_(False)
            raise ValueError(f"Unsupported unary operator: {expr.op}")

        if expr.type == ExprType.IN_LIST:
            assert expr.left is not None
            return self._compile_expr(expr.left).isin([self._compile_expr(v) for v in expr.args])

        if expr.type == ExprType.FUNCTION:
            func_name = expr.value.upper()
            if (_method_name := FUNC_MAP.get(func_name)) and expr.args:
                col = self._compile_expr(expr.args[0])
                if hasattr(col, _method_name):
                    return getattr(col, _method_name)()

            raise ValueError(f"Unsupported function: {func_name}")

        raise ValueError(f"Unsupported expression type: {expr.type}")

    def _infer_name(self, expr: ParsedExpr) -> str:
        if expr.type == ExprType.COLUMN:
            return expr.value
        if expr.type == ExprType.FUNCTION:
            if expr.args and expr.args[0].type == ExprType.COLUMN:
                return f"{expr.value.lower()}_{expr.args[0].value}"
            return expr.value.lower()
        return "expr"


def sql_query(query: str, table: Table) -> Table:
    return SQLCompiler().compile(SQLParser().parse(query), table)


class SQLQuery:
    def __init__(self, table: str, query: str) -> None:
        self.table_name = table
        self.query_str = query
        self._parsed = SQLParser().parse(query)

    @property
    def ipc(self):
        from rayforce.types.table import Table

        return SQLIPCCompiler().compile(self._parsed, Table(self.table_name)).ipc


class SQLIPCCompiler(SQLCompiler):
    def _compile_select(self, parsed: ParsedSelect, table: Table):
        select_args: list[str] = []
        select_kwargs: dict[str, t.Any] = {}

        for alias, expr in parsed.columns:
            if expr.type == ExprType.STAR:
                select_args.append("*")
            elif expr.type == ExprType.COLUMN and alias is None:
                select_args.append(expr.value)
            else:
                name = alias if alias else self._infer_name(expr)
                select_kwargs[name] = self._compile_expr(expr)

        query = (
            table.select(*select_args, **select_kwargs)
            if select_args or select_kwargs
            else table.select("*")
        )

        if _where := parsed.where_clause:
            query = query.where(self._compile_expr(_where))

        if _by := parsed.group_by:
            query = query.by(*_by)

        if _order := parsed.order_by:
            desc = any(is_desc for _, is_desc in _order)
            query = query.order_by(*[col for col, _ in _order], desc=desc)

        return query

    def _compile_update(self, parsed: ParsedUpdate, table: Table):
        update_kwargs: dict[str, t.Any] = {
            col_name: self._compile_expr(expr) for col_name, expr in parsed.assignments.items()
        }

        query = table.update(**update_kwargs)
        if _where := parsed.where_clause:
            query = query.where(self._compile_expr(_where))

        return query

    def _compile_insert(self, parsed: ParsedInsert, table: Table):
        compiled_rows: list[list[t.Any]] = [
            [self._compile_expr(val) for val in row] for row in parsed.values
        ]

        if _columns := parsed.columns:
            insert_kwargs: dict[str, list[t.Any]] = {col: [] for col in _columns}
            for row in compiled_rows:
                for i, col in enumerate(parsed.columns):
                    insert_kwargs[col].append(row[i])
            return table.insert(**insert_kwargs)

        if len(compiled_rows) == 1:
            return table.insert(*compiled_rows[0])

        return table.insert(
            *[[row[i] for row in compiled_rows] for i in range(len(compiled_rows[0]))]
        )

    def _compile_upsert(self, parsed: ParsedUpsert, table: Table):
        compiled_rows: list[list[t.Any]] = [
            [self._compile_expr(val) for val in row] for row in parsed.values
        ]

        if _columns := parsed.columns:
            upsert_kwargs: dict[str, list[t.Any]] = {col: [] for col in _columns}
            for row in compiled_rows:
                for i, col in enumerate(parsed.columns):
                    upsert_kwargs[col].append(row[i])
            return table.upsert(**upsert_kwargs, key_columns=parsed.key_columns)

        if len(compiled_rows) == 1:
            return table.upsert(*compiled_rows[0], key_columns=parsed.key_columns)

        return table.upsert(
            *[[row[i] for row in compiled_rows] for i in range(len(compiled_rows[0]))],
            key_columns=parsed.key_columns,
        )
