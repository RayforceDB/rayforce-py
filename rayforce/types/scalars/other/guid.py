from __future__ import annotations

import uuid

from rayforce import _rayforce_c as r
from rayforce.core.ffi import FFI
from rayforce.types.base import Scalar
from rayforce.types.registry import TypeRegistry


class GUID(Scalar):
    type_code = -r.TYPE_GUID
    ray_name = "guid"

    def _create_from_value(self, value: uuid.UUID | str | bytes) -> r.RayObject:
        return FFI.init_guid(value)

    def to_python(self) -> uuid.UUID:
        return uuid.UUID(bytes=FFI.read_guid(self.ptr))

    def __str__(self) -> str:
        return str(self.to_python())


TypeRegistry.register(-r.TYPE_GUID, GUID)
