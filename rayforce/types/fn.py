from __future__ import annotations

import typing as t

from rayforce import _rayforce_c as r
from rayforce import utils
from rayforce.types import Dict, List
from rayforce.types.base import RayObject
from rayforce.types.operators import Operation
from rayforce.types.registry import TypeRegistry
from rayforce.utils import evaluation

if t.TYPE_CHECKING:
    from rayforce.types.table import Expression


class Fn(RayObject):
    ptr: r.RayObject
    type_code = r.TYPE_LAMBDA
    ray_name = "LAMBDA"

    @classmethod
    def _create_from_value(cls, value: str) -> r.RayObject:
        if not isinstance(value, str):
            raise TypeError(f"Expected string, got {type(value)}")
        if not value.startswith("(fn"):
            raise ValueError("Provided string is not a fn expression")

        return evaluation.eval_str(value, raw=True)

    @classmethod
    def from_ptr(cls, ptr: r.RayObject) -> Fn:
        return cls(ptr=ptr)

    def apply(self, *args: t.Any) -> Expression:
        from rayforce.types.table import Expression

        return Expression(self, *args)

    def to_python(self) -> str:
        return str(self)

    @property
    def _meta(self) -> Dict:
        return utils.eval_obj(List([Operation.META, self]))

    def __str__(self) -> str:
        return str(self._meta["body"])

    def __repr__(self) -> str:
        meta = self._meta
        return f"Fn(args: {meta['args'].to_python()}; body: {meta['body'].to_python()})"

    def __call__(self, *args: t.Any) -> t.Any:
        return utils.eval_obj(self.apply(*args).compile())


TypeRegistry.register(r.TYPE_LAMBDA, Fn)
