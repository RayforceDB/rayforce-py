from __future__ import annotations

import typing as t

from rayforce import errors

if t.TYPE_CHECKING:
    from rayforce import _rayforce_c as r


def validate_port(port: int) -> None:
    if not isinstance(port, int) or port < 1 or port > 65535:
        raise errors.RayforceValueError(f"Invalid port: {port}. Must be between 1 and 65535")


def python_to_ipc(data: t.Any) -> r.RayObject:
    from rayforce import List, String, errors
    from rayforce.types.table import (
        AsofJoin,
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
    if isinstance(data, (List, String)):
        return data.ptr
    if isinstance(data, Expression):
        return data.compile()
    if isinstance(
        data,
        (
            SelectQuery,
            UpdateQuery,
            InsertQuery,
            UpsertQuery,
            AsofJoin,
            LeftJoin,
            InnerJoin,
            WindowJoin,
            WindowJoin1,
        ),
    ):
        return data.ipc
    raise errors.RayforceTCPError(f"Unsupported IPC data to send: {type(data)}")
