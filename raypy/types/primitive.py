import enum

from raypy import api
from raypy import _rayforce as r


class Operation(enum.StrEnum):
    # Math
    ADD = "+"
    SUBSTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    FDIVIDE = "fdiv"
    MODULO = "%"
    SUM = "sum"
    AVG = "avg"
    MEDIAN = "med"
    DEVIATION = "dev"
    MIN = "min"
    MAX = "max"
    CEIL = "ceil"
    FLOOR = "floor"
    ROUND = "round"
    XBAR = "xbar"

    # Database operations
    SELECT = "select"

    # Comparison
    EQUALS = "=="
    NOT_EQUALS = "!="
    GE = ">"
    GTE = ">="
    LE = "<"
    LTE = "<="

    # Misc
    DO = "do"
    QUOTE = "quote"
    IF = "IF"

    @property
    def primitive(self) -> r.RayObject:
        return api.env_get_internal_function_by_name(self.value)

    @property
    def is_binary(self) -> bool:
        return self.value.get_obj_type() == r.TYPE_BINARY

    @property
    def is_unary(self) -> bool:
        return self.value.get_obj_type() == r.TYPE_UNARY

    @property
    def is_vary(self) -> bool:
        return self.value.get_obj_type() == r.TYPE_VARY

    @staticmethod
    def from_ptr(obj: r.RayObject) -> "Operation":
        if (_type := obj.get_obj_type()) not in (
            r.TYPE_UNARY,
            r.TYPE_BINARY,
            r.TYPE_VARY,
        ):
            raise ValueError(f"Invalid object type for Operation - {_type}")

        try:
            name = api.env_get_internal_name_by_function(obj)
            return Operation(name)
        except ValueError:
            raise ValueError(f"Unknown operation - {name}")
