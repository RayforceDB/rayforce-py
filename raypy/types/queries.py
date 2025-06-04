import enum
from typing import Any
from dataclasses import dataclass
from raypy.types import container as c
from raypy.types import scalar as s
from raypy import _rayforce as r

GET_PRIMITIVE_METHOD = 'rayforce_env_get_internal_function'

class Operand(enum.StrEnum):
    multiply = '*'


@dataclass(frozen=True)
class SubQuery:
    operand: Operand
    first_arg: Any
    second_arg: Any

    def to_rf(self) -> c.List:
        primitive = getattr(r.RayObject, GET_PRIMITIVE_METHOD)(self.operand.value)
        return c.List([primitive, self.first_arg, self.second_arg])


class Query(c.Dict):
    def __init__(
        self,
        value: dict[str, Any] | None = None,
        *,
        ray_obj: Any | None = None,
    ) -> None:
        super().__init__(value, ray_obj=ray_obj)


{
    'key': 'value' / operation [what x y]
}


def select(
    query: dict[str, str | SubQuery],
    *,
    select_from: str,
    where: SubQuery | None = None,
) -> Query:
    res = {'from': select_from, 'where': where.to_rf(),}
    

    


def execute(query: Query):

    ...

