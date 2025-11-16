import enum

from raypy.core import FFI
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
    IJ = "inner-join"
    WJ = "window-join"
    WJ1 = "window-join1"
    WHERE = "where"
    DISTINCT = "distinct"
    CONCAT = "concat"
    FIRST = "first"
    LAST = "last"
    IN = "in"

    # Sort
    ASC = "asc"
    DESC = "desc"
    XASC = "xasc"
    XDESC = "xdesc"

    # Compose
    TIL = "til"

    # Comparison
    EQUALS = "=="
    NOT_EQUALS = "!="
    GE = ">"
    GTE = ">="
    LE = "<"
    LTE = "<="

    # Accessors
    AT = "at"

    # Type conversion
    LIST = "list"

    # Misc
    DO = "do"
    QUOTE = "quote"
    IF = "IF"
    COUNT = "count"
    AND = "and"
    OR = "or"
    MAP = "map"
    MAP_LEFT = "map-left"

    @property
    def primitive(self) -> r.RayObject:
        return FFI.env_get_internal_function_by_name(self.value)

    @property
    def is_binary(self) -> bool:
        return self.primitive.get_obj_type() == r.TYPE_BINARY

    @property
    def is_unary(self) -> bool:
        return self.primitive.get_obj_type() == r.TYPE_UNARY

    @property
    def is_vary(self) -> bool:
        return self.primitive.get_obj_type() == r.TYPE_VARY

    @staticmethod
    def from_ptr(obj: r.RayObject) -> "Operation":
        if (_type := obj.get_obj_type()) not in (
            r.TYPE_UNARY,
            r.TYPE_BINARY,
            r.TYPE_VARY,
        ):
            raise ValueError(f"Invalid object type for Operation - {_type}")

        try:
            name = FFI.env_get_internal_name_by_function(obj)
            return Operation(name)
        except ValueError:
            raise ValueError(f"Unknown operation - {name}")
