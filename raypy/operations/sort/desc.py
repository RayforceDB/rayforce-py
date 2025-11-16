import typing as t

from raypy import misc
from raypy.types.container import List
from raypy.types.operators import Operation


def desc(object: t.Any) -> t.Any:
    return misc.eval_obj(List([Operation.DESC, object]).ptr)
