from raypy.api.exceptions import c_api_exception_handler
from raypy import _rayforce as r


@c_api_exception_handler
def select(query: r.RayObject) -> r.RayObject:
    return r.select(query)


@c_api_exception_handler
def update(query: r.RayObject) -> r.RayObject:
    return r.update(query)


@c_api_exception_handler
def upsert(
    table_obj: r.RayObject, keys_obj: r.RayObject, data_obj: r.RayObject
) -> r.RayObject:
    return r.upsert(table_obj, keys_obj, data_obj)


@c_api_exception_handler
def insert(table_obj: r.RayObject, data_obj: r.RayObject) -> r.RayObject:
    return r.insert(table_obj, data_obj)
