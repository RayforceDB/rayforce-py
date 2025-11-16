from __future__ import annotations
import enum

from raypy import _rayforce as r
from raypy.core import FFI


class Operation(enum.StrEnum):
    # Arithmetic
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    FDIVIDE = "fdiv"
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
    ABS = "abs"
    
    # Collection 
    IN = "in"
    DISTINCT = "distinct"
    UNIQUE = "unique"
    
    # Query 
    SELECT = "select"
    WHERE = "where"
    GROUP_BY = "group-by"
    ORDER_BY = "order-by"
    
    # Join 
    INNER_JOIN = "inner-join"
    IJ = "inner-join" 
    WINDOW_JOIN = "window-join"
    WJ = "window-join"
    WINDOW_JOIN1 = "window-join1"
    WJ1 = "window-join1"
    
    # Sort
    ASC = "asc"
    DESC = "desc"
    XASC = "xasc"
    XDESC = "xdesc"
    
    # Accessor
    AT = "at"
    
    # Functional
    MAP = "map"
    MAP_LEFT = "map-left"
    EACH = "each"
    
    # Composition
    TIL = "til"
    
    # Type
    LIST = "list"
    VECTOR = "vector"
    
    # Other 
    QUOTE = "quote"
    CONCAT = "concat"
    JOIN_STRINGS = "join"
    
    @property
    def primitive(self) -> r.RayObject:
        """
        Get the underlying primitive (RayObject) function from the runtime.
        """
        return FFI.env_get_internal_function_by_name(self.value)
    
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
        obj_type = obj.get_obj_type()
        if obj_type not in (r.TYPE_UNARY, r.TYPE_BINARY, r.TYPE_VARY):
            raise ValueError(f"Object is not an operation (type: {obj_type})")

        return Operation(FFI.env_get_internal_name_by_function(obj))
