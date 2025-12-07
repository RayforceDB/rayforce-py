from __future__ import annotations

import datetime as dt
import typing as t
import uuid

from rayforce import _rayforce_c as r
from rayforce.types import exceptions
from rayforce.types.operators import Operation
from rayforce.types.registry import TypeRegistry

if t.TYPE_CHECKING:
    from rayforce.types.base import RayObject


def python_to_ray(value: t.Any, ray_type: type[RayObject] | None = None) -> r.RayObject:
    from rayforce.types import (
        B8,
        F64,
        GUID,
        I64,
        Date,
        Dict,
        List,
        Symbol,
        Table,
        Time,
        Timestamp,
    )

    if (
        hasattr(value, "ptr")
        and isinstance(value.ptr, r.RayObject)
        and not isinstance(value, Table)
    ):
        return value.ptr

    if value is None:
        # TODO: Return a special null value if available
        # For now, create an empty list as placeholder
        return List([]).ptr

    if ray_type is not None and not isinstance(ray_type, int):
        return ray_type(value).ptr

    if isinstance(value, r.RayObject):
        return value
    if isinstance(value, Operation):
        return value.primitive
    if isinstance(value, bool):
        return B8(value).ptr
    if isinstance(value, int):
        return I64(value).ptr
    if isinstance(value, float):
        return F64(value).ptr
    if isinstance(value, dt.datetime):
        return Timestamp(value).ptr
    if isinstance(value, dt.date):
        return Date(value).ptr
    if isinstance(value, dt.time):
        return Time(value).ptr
    if isinstance(value, uuid.UUID):
        return GUID(value).ptr
    if isinstance(value, str):
        return Symbol(value).ptr
    if isinstance(value, dict):
        return Dict(value).ptr
    if isinstance(value, (list, tuple)):
        return List(value).ptr

    raise exceptions.RayConversionError(
        f"Cannot convert Python type {type(value).__name__} to RayObject"
    )


def ray_to_python(ray_obj: r.RayObject) -> t.Any:
    if not isinstance(ray_obj, r.RayObject):
        raise exceptions.RayConversionError(f"Expected RayObject, got {type(ray_obj)}")

    try:
        return TypeRegistry.from_ptr(ray_obj)
    except Exception as e:
        raise exceptions.RayConversionError(f"Failed to convert RayObject: {e}") from e
