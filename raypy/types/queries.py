from __future__ import annotations
import enum
from typing import Any
from raypy.types import container as c
from raypy.types import scalar as s
from raypy import _rayforce as r

GET_PRIMITIVE_METHOD = "rayforce_env_get_internal_function"


class QueryOperation(enum.StrEnum):
    sum = "+"
    sub = "-"
    multiply = "*"
    div = "/"

    select = "select"
    min = "min"
    avg = "avg"

    ge = ">"

    @property
    def require_one_operand(self) -> bool:
        return self in (QueryOperation.select,)

    @property
    def require_two_operands(self) -> bool:
        return self in (
            QueryOperation.sum,
            QueryOperation.sub,
            QueryOperation.multiply,
            QueryOperation.div,
        )


class Expression:
    expression: c.List

    def __init__(
        self,
        operation: QueryOperation,
        operand_1: Any | None = None,
        operand_2: Any | None = None,
    ) -> None:
        if operation.require_two_operands and not all(
            [operand_1 is not None, operand_2 is not None]
        ):
            raise ValueError(f"Two operands are required for {operation}.")

        if (
            operation.require_one_operand
            and all([operand_1 is not None, operand_2 is not None])
            and all([operand_1 is None, operand_2 is None])
        ):
            raise ValueError(f"Single operand is required for {operation}.")

        expression = c.List()

        try:
            operation_primitive = r.env_get_internal_function(operation.value)
        except Exception as e:
            raise ValueError(f"Operation {operation.value} is undefined.") from e

        expression.append(operation_primitive)

        if operand_1 is not None:
            expression.append(operand_1)

        if operand_2 is not None:
            expression.append(operand_2)

        self.expression = expression

    def __str__(self) -> str:
        return f"Expression[{', '.join([str(i) for i in self.expression])}]"

    def __repr__(self) -> str:
        return self.__str__()


class SelectQuery:
    query: c.Dict

    def __init__(
        self,
        attributes: dict[str, Any],
        select_from: str | SelectQuery,
        where: Expression | None = None,
    ) -> None:
        keys = attributes.keys()
        values = attributes.values()

        if where is not None:
            query_keys = c.Vector(s.Symbol, len(keys) + 2)
        else:
            query_keys = c.Vector(s.Symbol, len(keys) + 1)

        query_values = c.List()

        for idx, key in enumerate(keys):
            query_keys[idx] = key

        for value in values:
            if isinstance(value, Expression):
                query_values.append(value.expression)
                continue
            query_values.append(value)

        query_keys[len(keys)] = "from"
        if isinstance(select_from, SelectQuery):
            query_values.append(
                c.List(
                    [
                        r.env_get_internal_function(QueryOperation.select.value),
                        select_from.query,
                    ]
                )
            )
        else:
            query_values.append(select_from)

        if where is not None:
            query_keys[len(keys) + 1] = "where"
            query_values.append(where.expression)

        try:
            query_ptr = r.RayObject.create_dict(query_keys.ptr, query_values.ptr)
            self.query = c.Dict(ray_obj=query_ptr)
        except Exception as e:
            raise ValueError("Error during Select type initialisation") from e


def select(q: SelectQuery) -> c.Table:
    result_ptr = r.RayObject.ray_select(q.query.ptr)

    if result_ptr.get_type() == r.TYPE_ERR:
        error_message = result_ptr.get_error_message()
        raise ValueError(f"Query error: {error_message}")

    if (_type := result_ptr.get_type()) != r.TYPE_TABLE:
        raise ValueError(f"Expected result of type Table (98), got {_type}")

    return c.Table(ray_obj=result_ptr)
