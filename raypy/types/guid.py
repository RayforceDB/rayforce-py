import uuid
from typing import Any

from raypy import _rayforce as r


class GUID:
    """
    Rayforce GUID type (Globally unique identifier)
    """

    ptr: r.RayObject

    ray_type_code = r.TYPE_GUID
    ray_init_method = "from_guid"
    ray_extr_method = "get_guid_value"

    def __init__(
        self,
        value: str | uuid.UUID | bytes | bytearray | None = None,
        ray_obj: r.RayObject | None = None,
    ) -> None:
        if ray_obj is not None:
            if (_type := ray_obj.get_type()) != self.ray_type_code:
                raise ValueError(
                    f"Expected RayForce object of type {self.ray_type_code}, got {_type}"
                )
            self.ptr = ray_obj
            return

        guid_bytes = None
        if value is None:
            guid_bytes = uuid.uuid4().bytes
        elif isinstance(value, uuid.UUID):
            guid_bytes = value.bytes
        elif isinstance(value, str):
            try:
                guid_bytes = uuid.UUID(value).bytes
            except ValueError as e:
                raise ValueError("Invalid GUID string format") from e
        elif isinstance(value, (bytes, bytearray)):
            if len(value) != 16:
                raise ValueError("GUID must be 16 bytes")
            guid_bytes = bytes(value)
        else:
            raise TypeError(f"Cannot convert {type(value)} to GUID")

        try:
            self.ptr = getattr(r.RayObject, self.ray_init_method)(guid_bytes)
            assert self.ptr is not None, "RayObject should not be empty"
        except Exception as e:
            raise TypeError(f"Error during type initialisation - {str(e)}")

    @property
    def __raw_bytes(self) -> bytes:
        try:
            return getattr(self.ptr, self.ray_extr_method)()
        except TypeError as e:
            raise TypeError(
                f"Expected RayObject type of {self.ray_type_code}, got {self.ptr.get_type()}"
            ) from e

    @property
    def value(self) -> uuid.UUID:
        return uuid.UUID(bytes=self.__raw_bytes)

    @property
    def hex(self) -> str:
        return self.value.hex

    @property
    def urn(self) -> str:
        return f"urn:uuid:{str(self.value)}"

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"GUID({self})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, GUID):
            return self.value == other.value
        if isinstance(other, uuid.UUID):
            return self.value == other
        if isinstance(other, str):
            try:
                return self.value == uuid.UUID(other)
            except ValueError:
                return False
        if isinstance(other, (bytes, bytearray)) and len(other) == 16:
            return self.__raw_bytes == bytes(other)

        return False
