from raypy import types as t
from raypy.core import FFI
from raypy import _rayforce as r


def insert(q: t.InsertQuery) -> t.Table | bool:
    result_ptr = FFI.insert(table_obj=q.insert_to_ptr, data_obj=q.insertable_ptr)
    result_type = result_ptr.get_obj_type()

    if result_type == r.TYPE_ERR:
        raise ValueError(f"Query error: {FFI.get_error_message(result_ptr)}")

    # Inplace insert does not return a table as result.
    if result_type == -r.TYPE_SYMBOL:
        return True

    if result_type != r.TYPE_TABLE:
        raise ValueError(f"Expected result of type Table (98), got {result_type}")

    return t.Table(ptr=result_ptr)
