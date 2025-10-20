from raypy import misc
from raypy import types as t


def window_join(
    join_by: t.Vector,
    to_join: list[t.Any],
    aggregation: t.Dict,
):
    return misc.eval_obj(t.List([t.Operation.WJ, join_by, *to_join, aggregation]).ptr)


def window_join1(
    join_by: t.Vector,
    to_join: list[t.Any],
    aggregation: t.Dict,
):
    return misc.eval_obj(t.List([t.Operation.WJ1, join_by, *to_join, aggregation]).ptr)
