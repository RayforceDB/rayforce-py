from __future__ import annotations
import uuid

from raypy import _rayforce as r
from raypy.core.ffi import FFI
from raypy.types.base import Scalar
from raypy.types.registry import TypeRegistry
from raypy.types import exceptions


class GUID(Scalar):
    """
    GUID/UUID type.
    """

    type_code = -r.TYPE_GUID
    ray_name = "GUID"

    def _create_from_value(self, value: uuid.UUID | str | bytes) -> r.RayObject:
        if isinstance(value, uuid.UUID):
            return FFI.init_guid(str(value))
        elif isinstance(value, str):
            return FFI.init_guid(str(uuid.UUID(value)))
        elif isinstance(value, bytes):
            return FFI.init_guid(str(uuid.UUID(bytes=value)))
        else:
            raise exceptions.RayInitException(f"Cannot create GUID from {type(value)}")

    def to_python(self) -> uuid.UUID:
        guid_bytes = FFI.read_guid(self.ptr)
        return uuid.UUID(bytes=guid_bytes)

    def __str__(self) -> str:
        return str(self.to_python())


TypeRegistry.register(-r.TYPE_GUID, GUID)
