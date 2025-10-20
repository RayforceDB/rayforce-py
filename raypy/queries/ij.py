from raypy import misc
from raypy import types as t


def inner_join(
    join_by: t.Vector,
    to_join: list[t.Any],
):
    return misc.eval_obj(t.List([t.Operation.IJ, join_by, *to_join]).ptr)
