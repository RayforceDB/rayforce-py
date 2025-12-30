from __future__ import annotations

import enum

from rayforce import _rayforce_c as r
from rayforce import errors
from rayforce.ffi import FFI
from rayforce.types.registry import TypeRegistry


class Operation(enum.StrEnum):
    # Arithmetic
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    DIV_INT = "div"
    NEGATE = "neg"

    # Comparison
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    GREATER_EQUAL = ">="
    LESS_THAN = "<"
    LESS_EQUAL = "<="
    LIKE = "like"

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
    ROW = "row"

    # Statistical
    XBAR = "xbar"

    # Math
    CEIL = "ceil"
    FLOOR = "floor"
    ROUND = "round"
    RAND = "rand"

    # Collection
    IN = "in"
    DISTINCT = "distinct"
    REVERSE = "reverse"
    GROUP = "group"
    TAKE = "take"
    REMOVE = "remove"
    FILTER = "filter"
    FIND = "find"
    WITHIN = "within"
    SECT = "sect"
    EXCEPT = "except"
    UNION = "union"
    RAZE = "raze"
    DIVERSE = "diverse"
    UNIFY = "unify"

    # Query
    SELECT = "select"
    UPDATE = "update"
    INSERT = "insert"
    UPSERT = "upsert"
    WHERE = "where"

    # Join
    INNER_JOIN = "inner-join"
    IJ = "inner-join"
    LEFT_JOIN = "left-join"
    LJ = "left-join"
    ASOF_JOIN = "asof-join"
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
    RANK = "rank"
    XRANK = "xrank"

    # Accessor
    AT = "at"
    KEY = "key"
    VALUE = "value"
    GET = "get"

    # Functional
    MAP = "map"
    MAP_LEFT = "map-left"
    MAP_RIGHT = "map-right"
    PMAP = "pmap"
    FOLD = "fold"
    FOLD_LEFT = "fold-left"
    FOLD_RIGHT = "fold-right"
    SCAN = "scan"
    SCAN_LEFT = "scan-left"
    SCAN_RIGHT = "scan-right"
    APPLY = "apply"
    ARGS = "args"
    ALTER = "alter"
    MODIFY = "modify"

    # Composition
    TIL = "til"
    ENLIST = "enlist"

    # Type
    LIST = "list"
    TYPE = "type"
    AS = "as"
    ENUM = "enum"
    GUID = "guid"
    NIL_Q = "nil?"

    # Temporal
    DATE = "date"
    TIME = "time"
    TIMESTAMP = "timestamp"

    # I/O
    READ = "read"
    WRITE = "write"
    READ_CSV = "read-csv"
    WRITE_CSV = "write-csv"
    HOPEN = "hopen"
    HCLOSE = "hclose"
    SHOW = "show"
    FORMAT = "format"
    PRINT = "print"
    PRINTLN = "println"

    # Serialization
    SER = "ser"
    DE = "de"
    PARSE = "parse"

    # Evaluation
    EVAL = "eval"
    QUOTE = "quote"
    LOAD = "load"
    RESOLVE = "resolve"

    # Control Flow
    DO = "do"
    IF = "if"
    TRY = "try"
    RETURN = "return"
    RAISE = "raise"

    # Variables
    SET = "set"
    LET = "let"
    ENV = "env"

    # Data Structures
    DICT = "dict"
    TABLE = "table"
    CONCAT = "concat"

    # System
    SYSTEM = "system"
    OS_GET_VAR = "os-get-var"
    OS_SET_VAR = "os-set-var"
    EXIT = "exit"
    GC = "gc"
    MEMSTAT = "memstat"
    TIMEIT = "timeit"
    TIMER = "timer"
    INTERNALS = "internals"
    SYSINFO = "sysinfo"
    LOADFN = "loadfn"

    # Storage
    SET_SPLAYED = "set-splayed"
    GET_SPLAYED = "get-splayed"
    SET_PARTED = "set-parted"
    GET_PARTED = "get-parted"

    # Metadata
    META = "meta"
    RC = "rc"

    # Binary operations
    BIN = "bin"
    BINR = "binr"
    SPLIT = "split"

    @property
    def primitive(self) -> r.RayObject:
        return FFI.env_get_internal_fn_by_name(self.value)

    @property
    def ptr(self) -> r.RayObject:
        return self.primitive

    @property
    def is_binary(self) -> bool:
        return FFI.get_obj_type(self.primitive) == r.TYPE_BINARY

    @property
    def is_unary(self) -> bool:
        return FFI.get_obj_type(self.primitive) == r.TYPE_UNARY

    @property
    def is_variadic(self) -> bool:
        return FFI.get_obj_type(self.primitive) == r.TYPE_VARY

    @staticmethod
    def from_ptr(obj: r.RayObject) -> Operation:
        if (obj_type := FFI.get_obj_type(obj)) not in (
            r.TYPE_UNARY,
            r.TYPE_BINARY,
            r.TYPE_VARY,
        ):
            raise errors.RayforceInitError(f"Object is not an operation (type: {obj_type})")

        return Operation(FFI.env_get_internal_name_by_fn(obj))


TypeRegistry.register(r.TYPE_UNARY, Operation)
TypeRegistry.register(r.TYPE_BINARY, Operation)
TypeRegistry.register(r.TYPE_VARY, Operation)
