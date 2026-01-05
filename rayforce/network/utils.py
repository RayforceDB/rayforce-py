from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    from rayforce import _rayforce_c as r


def python_to_ipc(data: t.Any) -> r.RayObject:
    from rayforce import List, Operation, String, errors
    from rayforce.types.table import (
        Expression,
        InnerJoin,
        InsertQuery,
        LeftJoin,
        SelectQuery,
        UpdateQuery,
        UpsertQuery,
        WindowJoin,
        WindowJoin1,
    )

    if isinstance(data, str):
        return String(data).ptr
    if isinstance(data, List):
        return data.ptr
    if isinstance(data, SelectQuery):
        return Expression(Operation.SELECT, data.compile()).compile()
    if isinstance(data, UpdateQuery):
        return Expression(Operation.UPDATE, data.compile()).compile()
    if isinstance(data, InsertQuery):
        return Expression(Operation.INSERT, data.table, data.compile()).compile()
    if isinstance(data, UpsertQuery):
        return Expression(Operation.UPSERT, data.table, *data.compile()).compile()
    if isinstance(data, LeftJoin):
        return Expression(Operation.LEFT_JOIN, *data.compile()).compile()
    if isinstance(data, InnerJoin):
        return Expression(Operation.INNER_JOIN, *data.compile()).compile()
    if isinstance(data, WindowJoin):
        return Expression(Operation.WINDOW_JOIN, *data.compile()).compile()
    if isinstance(data, WindowJoin1):
        return Expression(Operation.WINDOW_JOIN1, *data.compile()).compile()
    raise errors.RayforceIPCError(f"Unsupported IPC data to send: {type(data)}")
