from raypy.api.exceptions import c_api_exception_handler
from raypy import _rayforce as r


@c_api_exception_handler
def hopen(host: r.RayObject, timeout: r.RayObject | None = None) -> r.RayObject:
    return r.hopen(host, timeout)


@c_api_exception_handler
def hclose(conn: r.RayObject) -> None:
    r.hclose(conn)


@c_api_exception_handler
def write(conn: r.RayObject, data: r.RayObject) -> r.RayObject:
    return r.write(conn, data)
