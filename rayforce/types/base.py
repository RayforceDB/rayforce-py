from __future__ import annotations

from abc import ABC, abstractmethod
import typing as t

from rayforce import _rayforce_c as r
from rayforce import errors
from rayforce.ffi import FFI


class RayObject(ABC):
    ptr: r.RayObject
    type_code: t.ClassVar[int]
    ray_name: t.ClassVar[str]

    def __init__(
        self,
        value: t.Any = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        if value is None and ptr is None:
            raise errors.RayforceInitError(
                f"{self.__class__.__name__} requires either 'value' or 'ptr' argument",
            )

        if ptr is not None:
            self._validate_ptr(ptr)
            self.ptr = ptr
        else:
            self.ptr = self._create_from_value(value)

    def _validate_ptr(self, ptr: r.RayObject) -> None:
        if not isinstance(ptr, r.RayObject):
            raise errors.RayforceInitError(f"Expected RayObject, got {type(ptr)}")

        if (
            hasattr(self.__class__, "type_code")
            and self.__class__.type_code is not None
            and (type_ := FFI.get_obj_type(ptr)) != self.__class__.type_code
        ):
            raise errors.RayforceInitError(
                f"{self.__class__.__name__} expects type code {self.__class__.type_code}, "
                f"got {type_}",
            )

    @abstractmethod
    def _create_from_value(self, value: t.Any) -> r.RayObject:
        raise NotImplementedError

    @abstractmethod
    def to_python(self) -> t.Any:
        raise NotImplementedError

    @classmethod
    def from_python(cls, value: t.Any) -> t.Self:
        return cls(value=value)

    @classmethod
    def from_ptr(cls, ptr: r.RayObject) -> t.Self:
        return cls(ptr=ptr)

    def get_type_code(self) -> int:
        return FFI.get_obj_type(self.ptr)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_python()!r})"

    def __str__(self) -> str:
        return str(self.to_python())

    def __eq__(self, other: t.Any) -> bool:
        if isinstance(other, RayObject):
            return self.to_python() == other.to_python()
        return self.to_python() == other

    def __hash__(self) -> int:
        try:
            return hash(self.to_python())
        except TypeError:
            return hash(id(self))


class Scalar(RayObject):
    @property
    def value(self) -> t.Any:
        return self.to_python()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"


class Container(RayObject):
    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError("Length method is not implemented for the type")

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError("Iter method is not implemented for the type")

    def __bool__(self) -> bool:
        return len(self) > 0
