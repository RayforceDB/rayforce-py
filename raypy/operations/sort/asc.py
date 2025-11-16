import typing as t

from raypy import misc
from raypy.types.container import List
from raypy.types.operators import Operation


def asc(object: t.Any) -> t.Any:
    return misc.eval_obj(List([Operation.ASC, object]).ptr)
