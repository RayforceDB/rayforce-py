from raypy import _rayforce as r
from raypy.core import FFI
from raypy import types as t


def select(q: t.SelectQuery) -> t.Table:
    """
    Perform select operation.
    """

    result_ptr = FFI.select(q.ptr)
    result_type = result_ptr.get_obj_type()

    if result_type == r.TYPE_ERR:
        raise ValueError(f"Query error: {FFI.get_error_message(result_ptr)}")

    if result_type != r.TYPE_TABLE:
        raise ValueError(f"Expected result of type Table (98), got {result_type}")

    return t.Table(ptr=result_ptr)
