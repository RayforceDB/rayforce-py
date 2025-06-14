from raypy import types as t
from raypy import _rayforce as r
from raypy import api


def update(q: t.UpdateQuery) -> t.Table | bool:
    """
    Perform update operation.
    """

    result_ptr = api.update(q.ptr)
    result_type = result_ptr.get_obj_type()

    if result_type == r.TYPE_ERR:
        raise ValueError(f"Query error: {api.get_error_message(result_ptr)}")

    # Inplace update does not return a table as result.
    if result_type == -r.TYPE_SYMBOL:
        return True

    if result_type != r.TYPE_TABLE:
        raise ValueError(f"Expected result of type Table (98), got {result_type}")

    return t.Table(ray_obj=result_ptr)
