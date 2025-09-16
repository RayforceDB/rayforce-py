import typing as t

from raypy import misc
from raypy.types.container import List, Vector
from raypy.types.primitive import Operation
from raypy.types.scalar import Symbol


def xasc(obj: t.Any, sort_by: list[str]) -> t.Any:
    _sort_by = Vector(type_code=Symbol.type_code, items=sort_by)
    return misc.eval_obj(List([Operation.XASC, obj, _sort_by]).ptr)
