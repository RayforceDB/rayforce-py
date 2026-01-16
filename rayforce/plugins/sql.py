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


class SQLParser:
    def parse(self, sql: str) -> ParsedSelect:
        sqlglot = _ensure_sqlglot()
        ast = sqlglot.parse_one(sql)

        if ast.key != "select":
            raise ValueError(f"Only SELECT statements are supported, got: {ast.key}")

        return self._parse_select(ast)

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
        if node.args.get("where"):
            where_clause = self._parse_expr(node.args["where"].this)

        group_by: list[str] = []
        if node.args.get("group"):
            for g in node.args["group"].expressions:
                if isinstance(g, exp.Column):
                    group_by.append(g.name)
                else:
                    group_by.append(str(g))

        order_by: list[tuple[str, bool]] = []
        if node.args.get("order"):
            for o in node.args["order"].expressions:
                is_desc = isinstance(o, exp.Ordered) and o.args.get("desc", False)
                col_expr = o.this if isinstance(o, exp.Ordered) else o
                if isinstance(col_expr, exp.Column):
                    order_by.append((col_expr.name, is_desc))
                else:
                    order_by.append((str(col_expr), is_desc))

        return ParsedSelect(
            columns=columns,
            where_clause=where_clause,
            group_by=group_by,
            order_by=order_by,
        )

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
            values = [self._parse_expr(v) for v in node.expressions]
            return ParsedExpr(
                type=ExprType.IN_LIST,
                left=self._parse_expr(node.this),
                args=values,
            )

        if isinstance(node, exp.Func):
            func_name = node.key.upper()
            args: list[ParsedExpr] = []

            if hasattr(node, "this") and node.this is not None:
                this_val = node.this
                if isinstance(this_val, exp.Expression):
                    args.append(self._parse_expr(this_val))

            if hasattr(node, "expressions") and node.expressions:
                for expr in node.expressions:
                    if isinstance(expr, exp.Expression):
                        args.append(self._parse_expr(expr))  # noqa: PERF401

            return ParsedExpr(type=ExprType.FUNCTION, value=func_name, args=args)

        raise ValueError(f"Unsupported SQL expression type: {type(node).__name__}")


class SQLCompiler:
    def compile(self, parsed: ParsedSelect, table: Table) -> Table:
        select_args: list[str] = []
        select_kwargs: dict[str, t.Any] = {}

        for alias, expr in parsed.columns:
            if expr.type == ExprType.STAR:
                select_args.append("*")
            elif expr.type == ExprType.COLUMN and alias is None:
                select_args.append(expr.value)
            else:
                compiled = self._compile_expr(expr)
                name = alias if alias else self._infer_name(expr)
                select_kwargs[name] = compiled

        if select_args or select_kwargs:
            query = table.select(*select_args, **select_kwargs)
        else:
            query = table.select("*")

        if parsed.where_clause:
            where_expr = self._compile_expr(parsed.where_clause)
            query = query.where(where_expr)

        if parsed.group_by:
            query = query.by(*parsed.group_by)

        if parsed.order_by:
            cols = [col for col, _ in parsed.order_by]

            desc = any(is_desc for _, is_desc in parsed.order_by)
            query = query.order_by(*cols, desc=desc)

        return query.execute()

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
            left = self._compile_expr(expr.left)
            right = self._compile_expr(expr.right)

            op_method = OP_MAP.get(expr.op)
            if op_method and hasattr(left, op_method):
                return getattr(left, op_method)(right)

            raise ValueError(f"Unsupported binary operator: {expr.op}")

        if expr.type == ExprType.UNARY_OP:
            assert expr.left is not None
            operand = self._compile_expr(expr.left)
            if expr.op == "NOT":
                return operand.is_(False)
            raise ValueError(f"Unsupported unary operator: {expr.op}")

        if expr.type == ExprType.IN_LIST:
            assert expr.left is not None
            col = self._compile_expr(expr.left)
            values = [self._compile_expr(v) for v in expr.args]
            return col.isin(values)

        if expr.type == ExprType.FUNCTION:
            func_name = expr.value.upper()
            method_name = FUNC_MAP.get(func_name)

            if method_name and expr.args:
                col = self._compile_expr(expr.args[0])
                if hasattr(col, method_name):
                    return getattr(col, method_name)()

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
