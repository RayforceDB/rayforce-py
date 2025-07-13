from typing import Any, Iterable
from raypy.types import container as c
from raypy import api
from raypy.types import primitive as p
from raypy.types import queries as q
from raypy import _rayforce as r


class Lambda:
    ptr: r.RayObject

    def __init__(
        self,
        arguments: list[str],
        expressions: Iterable[q.Expression],
    ) -> None:
        lambda_args = api.init_vector(type_code=-r.TYPE_SYMBOL, length=len(arguments))
        for idx, arg in enumerate(arguments):
            api.insert_obj(
                source_obj=lambda_args,
                idx=idx,
                value=api.from_python_to_rayforce_type(arg),
            )

        lambda_expression = api.init_list()
        api.push_obj_to_iterable(
            iterable=lambda_expression,
            obj=p.Operation.DO.primitive,
        )
        for expr in expressions:
            if len(expr) == 1:
                api.push_obj_to_iterable(
                    iterable=lambda_expression,
                    obj=expr[0].ptr,
                )
                continue
            api.push_obj_to_iterable(
                iterable=lambda_expression,
                obj=expr.ptr,
            )

        self.ptr = api.init_lambda(lambda_args, lambda_expression)

    @property
    def args(self) -> c.Vector:
        return c.from_rf_to_raypy(api.get_lambda_args(self.ptr))

    @property
    def body(self) -> Any:
        return c.from_rf_to_raypy(api.get_lambda_body(self.ptr))

    def __str__(self) -> str:
        return f"Lambda with arguments ({[i for i in self.args]}) and body {[i for i in self.body]}"

    def __repr__(self) -> str:
        return self.__str__()

    def call(self, *args) -> Any:
        result_ptr = api.lambda_call(
            self.ptr, *[api.from_python_to_rayforce_type(arg) for arg in args]
        )

        if result_ptr.get_obj_type() == r.TYPE_ERR:
            raise ValueError(f"Query error: {api.get_error_message(result_ptr)}")

        return c.from_rf_to_raypy(result_ptr)
