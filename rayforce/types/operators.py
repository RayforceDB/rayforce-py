from __future__ import annotations
import enum

from rayforce import _rayforce_c as r
from rayforce.core import FFI
from rayforce.types.registry import TypeRegistry


class Operation(enum.StrEnum):
    # Arithmetic
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    NEGATE = "neg"

    # Comparison
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    GREATER_EQUAL = ">="
    LESS_THAN = "<"
    LESS_EQUAL = "<="

    # Logical
    AND = "and"
    OR = "or"
    NOT = "not"

    # Aggregation
    SUM = "sum"
    AVG = "avg"
    MEAN = "avg"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    FIRST = "first"
    LAST = "last"
    MEDIAN = "med"
    DEVIATION = "dev"

    # Statistical
    XBAR = "xbar"

    # Math
    CEIL = "ceil"
    FLOOR = "floor"
    ROUND = "round"

    # Collection
    IN = "in"
    DISTINCT = "distinct"

    # Query
    SELECT = "select"
    INSERT = "insert"
    WHERE = "where"

    # Join
    INNER_JOIN = "inner-join"
    IJ = "inner-join"
    LEFT_JOIN = "left-join"
    LJ = "left-join"
    WINDOW_JOIN = "window-join"
    WJ = "window-join"
    WINDOW_JOIN1 = "window-join1"
    WJ1 = "window-join1"

    # Sort
    ASC = "asc"
    DESC = "desc"
    XASC = "xasc"
    XDESC = "xdesc"
    IASC = "iasc"
    IDESC = "idesc"

    # Accessor
    AT = "at"

    # Functional
    MAP = "map"
    MAP_LEFT = "map-left"

    # Composition
    TIL = "til"

    # Type
    LIST = "list"

    # Other
    EVAL = "eval"
    QUOTE = "quote"
    CONCAT = "concat"
    READ_CSV = "read-csv"
    SET = "set"

    @property
    def primitive(self) -> r.RayObject:
        return FFI.env_get_internal_function_by_name(self.value)

    @property
    def ptr(self) -> r.RayObject:
        return self.primitive

    @property
    def is_binary(self) -> bool:
        return self.primitive.get_obj_type() == r.TYPE_BINARY

    @property
    def is_unary(self) -> bool:
        return self.primitive.get_obj_type() == r.TYPE_UNARY

    @property
    def is_variadic(self) -> bool:
        return self.primitive.get_obj_type() == r.TYPE_VARY

    @staticmethod
    def from_ptr(obj: r.RayObject) -> Operation:
        if (obj_type := obj.get_obj_type()) not in (
            r.TYPE_UNARY,
            r.TYPE_BINARY,
            r.TYPE_VARY,
        ):
            raise ValueError(f"Object is not an operation (type: {obj_type})")

        return Operation(FFI.env_get_internal_name_by_function(obj))


TypeRegistry.register(r.TYPE_UNARY, Operation)
TypeRegistry.register(r.TYPE_BINARY, Operation)
TypeRegistry.register(r.TYPE_VARY, Operation)
