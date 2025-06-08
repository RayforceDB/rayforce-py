from raypy import _rayforce as r
from raypy import api
from raypy import types as t


def select(q: t.SelectQuery) -> t.Table:
    result_ptr = api.select(q.ptr)

    if result_ptr.get_obj_type() == r.TYPE_ERR:
        raise ValueError(f"Query error: {api.get_error_message(result_ptr)}")

    if (_type := result_ptr.get_obj_type()) != r.TYPE_TABLE:
        raise ValueError(f"Expected result of type Table (98), got {_type}")

    return t.Table(ray_obj=result_ptr)
