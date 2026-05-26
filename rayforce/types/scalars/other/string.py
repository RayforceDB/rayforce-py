from __future__ import annotations

import typing as t

import numpy as np

from rayforce import _rayforce_c as r
from rayforce import errors
from rayforce.ffi import FFI
from rayforce.types.base import Scalar
from rayforce.types.registry import TypeRegistry

if t.TYPE_CHECKING:
    from rayforce.types.containers.vector import Vector


class String(Scalar):
    """v2 string atom (type -RAY_STR).

    Stored as a single RayObject atom — SSO for ≤7 bytes, pooled otherwise.
    Exposes len/iter/index helpers so call sites written against the old
    C8-vector shape continue to work at the Python layer.
    """

    type_code = -r.TYPE_STR
    ray_name = "str"

    def __init__(
        self,
        value: str | String | Vector | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        # Aliasing shortcut: String(other_string_or_vec) shares the ptr.
        # Vector imported lazily — vector.py loads symbol → scalars/other/
        # which triggers string.py mid-init, so a top-level import deadlocks.
        from rayforce.types.containers.vector import Vector

        if ptr is None and isinstance(value, (String, Vector)):
            super().__init__(ptr=value.ptr)
        else:
            super().__init__(value=value, ptr=ptr)

    def _create_from_value(self, value: t.Any) -> r.RayObject:
        if not isinstance(value, str):
            raise errors.RayforceInitError(f"String expects str, got {type(value).__name__}")
        return FFI.init_string(value)

    def _validate_ptr(self, ptr: r.RayObject) -> None:
        if not isinstance(ptr, r.RayObject):
            raise errors.RayforceInitError(f"Expected RayObject, got {type(ptr)}")
        actual = FFI.get_obj_type(ptr)
        # Accept canonical -RAY_STR atom or a +RAY_STR vector wrapping one.
        if actual not in (self.type_code, r.TYPE_STR):
            raise errors.RayforceInitError(f"Expected String (type {self.type_code}), got {actual}")

    def to_python(self) -> str:  # type: ignore[override]
        return FFI.read_string(self.ptr)

    def __len__(self) -> int:
        return FFI.get_obj_length(self.ptr)

    def __bool__(self) -> bool:
        return len(self) > 0

    def __getitem__(self, idx: int) -> String:
        py = self.to_python()
        if idx < 0:
            idx = len(py) + idx
        if idx < 0 or idx >= len(py):
            raise errors.RayforceIndexError(f"String index out of range: {idx}")
        return String(py[idx])

    def __iter__(self) -> t.Iterator[String]:
        for ch in self.to_python():
            yield String(ch)

    def to_numpy(self) -> t.Any:
        return np.array(list(self.to_python()))


TypeRegistry.register(-r.TYPE_STR, String)
