from __future__ import annotations


from raypy import _rayforce as r
from raypy.types import scalar as s
from raypy.types import container as c
from raypy.queries import expr


class SelectQuery:
    """
    Type which represents ready-to-run Rayforce query.

    This type should be passed to select() function to be executed.
    """

    query: c.Dict

    @staticmethod
    def __validate(
        attributes: dict[s.Symbol | str, s.Symbol | str | expr.Expression],
        select_from: str | s.Symbol | SelectQuery,
        where: expr.Expression | None = None,
    ) -> tuple[list[s.Symbol | str], list[s.Symbol | str | expr.Expression], int]:
        if not select_from:
            raise ValueError("Attribute select_from is required.")

        keys = attributes.keys()
        values = attributes.values()
        key_vector_length = len(keys) + 1  # select_from as +1

        if any([not isinstance(key, (str, s.Symbol)) for key in keys]):
            raise ValueError("Query keys should be Python strings or Raypy symbols.")

        if any(
            [
                not isinstance(value, (str, s.Symbol, expr.Expression))
                for value in values
            ]
        ):
            raise ValueError(
                "Query values should be Python strings or Raypy symbols or Raypy expression."
            )

        if where is not None:
            key_vector_length += 1
            if not isinstance(where, expr.Expression):
                raise ValueError("Attribute where should be an Expression.")

        return keys, values, key_vector_length

    def __init__(
        self,
        attributes: dict[s.Symbol | str, s.Symbol | str | expr.Expression],
        select_from: str | s.Symbol | SelectQuery,
        where: expr.Expression | None = None,
    ) -> None:
        keys, values, key_vector_length = self.__validate(
            attributes, select_from, where
        )

        # Build query keys and values out of original given attributes
        query_keys = c.Vector(s.Symbol, key_vector_length)
        query_values = c.List()

        for idx, key in enumerate(keys):
            query_keys[idx] = key

        for value in values:
            if isinstance(value, expr.Expression):
                query_values.append(value.expression)
                continue
            query_values.append(value)

        # Append `select_from`` attribute to the query
        query_keys[len(keys)] = "from"
        if isinstance(select_from, SelectQuery):
            query_values.append(
                expr.Expression(
                    expr.QueryOperation.select, select_from.query
                ).expression
            )
        else:
            query_values.append(select_from)

        # Append `where`` attribute to the query
        if where is not None:
            query_keys[len(keys) + 1] = "where"
            query_values.append(where.expression)

        # Build the actual query
        try:
            query_ptr = r.init_dict(query_keys.ptr, query_values.ptr)
            self.query = c.Dict(ray_obj=query_ptr)
        except Exception as e:
            raise ValueError("Error during Select type initialisation") from e


def select(q: SelectQuery) -> c.Table:
    result_ptr = r.select(q.query.ptr)

    if result_ptr.get_obj_type() == r.TYPE_ERR:
        raise ValueError(f"Query error: {result_ptr.get_error_message()}")

    if (_type := result_ptr.get_obj_type()) != r.TYPE_TABLE:
        raise ValueError(f"Expected result of type Table (98), got {_type}")

    return c.Table(ray_obj=result_ptr)
