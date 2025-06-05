from __future__ import annotations

import enum
from typing import Any

from raypy import _rayforce as r
from raypy.types import container as c


class QueryOperation(enum.StrEnum):
    """
    Mapping of typed query operations to Rayforce primitive functions.
    """

    # Math operations
    add = "+"
    substract = "-"
    multiply = "*"
    divide = "/"
    fdivide = "div"
    modulo = "%"
    sum = "sum"
    average = "avg"
    median = "med"
    deviation = "dev"
    min = "min"
    max = "max"
    ceil = "ceil"
    floor = "floor"
    round = "round"
    xbar = "xbar"

    # Database operations
    select = "select"

    # Comparison operations
    eq = "=="
    neq = "!="
    ge = ">"
    gte = ">="
    le = "<"
    lte = "<="

    @property
    def require_one_operand(self) -> bool:
        return self in (
            QueryOperation.sum,
            QueryOperation.average,
            QueryOperation.median,
            QueryOperation.deviation,
            QueryOperation.min,
            QueryOperation.max,
            QueryOperation.ceil,
            QueryOperation.floor,
            QueryOperation.round,
            QueryOperation.xbar,
            QueryOperation.select,
        )

    @property
    def require_two_operands(self) -> bool:
        return self in (
            QueryOperation.sum,
            QueryOperation.substract,
            QueryOperation.multiply,
            QueryOperation.divide,
            QueryOperation.fdivide,
            QueryOperation.modulo,
            QueryOperation.eq,
            QueryOperation.neq,
            QueryOperation.ge,
            QueryOperation.gte,
            QueryOperation.le,
            QueryOperation.lte,
        )

    @property
    def primitive(self) -> r.RayObject:
        try:
            return r.env_get_internal_function(self.value)
        except Exception as e:
            raise ValueError(f"Operation {self.value} is undefined.") from e

    @staticmethod
    def from_ptr(ptr: r.RayObject) -> QueryOperation:
        internal_name = r.env_get_internal_name(ptr)

        try:
            return QueryOperation(internal_name)
        except ValueError:
            raise ValueError(f"Unknown QueryOperation - {internal_name}")

    def __str__(self) -> str:
        try:
            return r.env_get_internal_name(self.primitive)
        except Exception as e:
            raise ValueError(f"Unable to get {self.value} internal name.") from e

    def __repr__(self) -> str:
        return self.__str__()


class Expression:
    """
    Raypy expression type, which is a List of 2(or 3) attributes, where
    first attribute is a primitive function and second (and third) attributes
    are operands.
    """

    expression: c.List

    @staticmethod
    def __validate_operands(
        operation: QueryOperation,
        x: Any | None = None,
        y: Any | None = None,
    ) -> None:
        if operation.require_two_operands:
            if x is None or y is None:
                raise ValueError(f"Two operands are required for {operation}.")

        elif operation.require_one_operand:
            if (x is not None and y is not None) or (x is None and y is None):
                raise ValueError(f"Exactly one operand is required for {operation}.")

    def __init__(
        self,
        operation: QueryOperation,
        x: Any | None = None,
        y: Any | None = None,
    ) -> None:
        self.__validate_operands(operation, x, y)

        # List which looks like [r.RayObject(primitive), x, y | null]
        expression = c.List([operation.primitive])
        if x is not None:
            expression.append(x)
        if y is not None:
            expression.append(y)

        self.expression = expression

    def __str__(self) -> str:
        return f"Expression[{', '.join([str(i) for i in self.expression])}]"

    def __repr__(self) -> str:
        return self.__str__()
