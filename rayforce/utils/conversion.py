from __future__ import annotations
import typing as t
import datetime as dt
import uuid

from rayforce import _rayforce_c as r
from rayforce.types.base import RayObject
from rayforce.types.operators import Operation
from rayforce.types.registry import TypeRegistry


class RayConversionError(Exception): ...


def python_to_ray(value: t.Any, ray_type: RayObject | None = None) -> r.RayObject:
    from rayforce.types import (
        I64,
        F64,
        B8,
        Date,
        Time,
        Timestamp,
        Symbol,
        GUID,
        List,
        Dict,
        Table,
    )

    if hasattr(value, "ptr") and isinstance(value.ptr, r.RayObject) and not isinstance(value, Table):
        return value.ptr

    if ray_type is not None and not isinstance(ray_type, int):
        return ray_type(value).ptr

    if isinstance(value, r.RayObject):
        return value
    elif isinstance(value, Operation):
        return value.primitive
    elif isinstance(value, bool):
        return B8(value).ptr
    elif isinstance(value, int):
        return I64(value).ptr
    elif isinstance(value, float):
        return F64(value).ptr
    elif isinstance(value, dt.datetime):
        return Timestamp(value).ptr
    elif isinstance(value, dt.date):
        return Date(value).ptr
    elif isinstance(value, dt.time):
        return Time(value).ptr
    elif isinstance(value, uuid.UUID):
        return GUID(value).ptr
    elif isinstance(value, str):
        return Symbol(value).ptr
    elif isinstance(value, dict):
        return Dict(value).ptr
    elif isinstance(value, (list, tuple)):
        return List(value).ptr
    elif value is None:
        # TODO: Return a special null value if available
        # For now, create an empty list as placeholder
        return List([]).ptr

    raise RayConversionError(
        f"Cannot convert Python type {type(value).__name__} to RayObject"
    )


def ray_to_python(ray_obj: r.RayObject) -> t.Any:
    if not isinstance(ray_obj, r.RayObject):
        raise RayConversionError(f"Expected RayObject, got {type(ray_obj)}")

    try:
        return TypeRegistry.from_ptr(ray_obj)
    except Exception as e:
        raise RayConversionError(f"Failed to convert RayObject: {e}") from e
