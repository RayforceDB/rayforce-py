from __future__ import annotations

from abc import ABC, abstractmethod
import typing as t

from rayforce import FFI, errors, utils
from rayforce import _rayforce_c as r


class RayObject(ABC):
    ptr: r.RayObject
    type_code: t.ClassVar[int]
    ray_name: t.ClassVar[str]

    def __init__(
        self,
        value: t.Any = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        if value is None and ptr is None:
            raise errors.RayforceInitError(
                f"{self.__class__.__name__} requires either 'value' or 'ptr' argument",
            )

        if ptr is not None:
            self._validate_ptr(ptr)
            self.ptr = ptr
        else:
            self.ptr = self._create_from_value(value)

    def _validate_ptr(self, ptr: r.RayObject) -> None:
        if not isinstance(ptr, r.RayObject):
            raise errors.RayforceInitError(f"Expected RayObject, got {type(ptr)}")

        if hasattr(self.__class__, "type_code") and self.__class__.type_code is not None:
            actual_type = FFI.get_obj_type(ptr)
            if actual_type != self.__class__.type_code:
                raise errors.RayforceInitError(
                    f"{self.__class__.__name__} expects type code {self.__class__.type_code}, "
                    f"got {actual_type}",
                )

    @abstractmethod
    def _create_from_value(self, value: t.Any) -> r.RayObject:
        raise NotImplementedError

    @abstractmethod
    def to_python(self) -> t.Any:
        raise NotImplementedError

    @classmethod
    def from_python(cls, value: t.Any) -> t.Self:
        return cls(value=value)

    @classmethod
    def from_ptr(cls, ptr: r.RayObject) -> t.Self:
        return cls(ptr=ptr)

    def get_type_code(self) -> int:
        return FFI.get_obj_type(self.ptr)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_python()!r})"

    def __str__(self) -> str:
        return str(self.to_python())

    def __eq__(self, other: t.Any) -> bool:
        if isinstance(other, RayObject):
            return self.to_python() == other.to_python()
        return self.to_python() == other

    def __hash__(self) -> int:
        try:
            return hash(self.to_python())
        except TypeError:
            return hash(id(self))


class Scalar(RayObject):
    @property
    def value(self) -> t.Any:
        return self.to_python()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"


class Container(RayObject):
    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError("Length method is not implemented for the type")

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError("Iter method is not implemented for the type")

    def __bool__(self) -> bool:
        return len(self) > 0


def _eval_operation(operation: str, *args: t.Any) -> t.Any:
    from rayforce import List, Operation

    return utils.eval_obj(List([getattr(Operation, operation), *args]))


class _AriphmeticMixin:
    def __add__(self, other) -> t.Any:
        return _eval_operation("ADD", self, other)

    def __radd__(self, other) -> t.Any:
        return _eval_operation("ADD", other, self)

    def __sub__(self, other) -> t.Any:
        return _eval_operation("SUBTRACT", self, other)

    def __rsub__(self, other) -> t.Any:
        return _eval_operation("SUBTRACT", other, self)

    def __mul__(self, other) -> t.Any:
        return _eval_operation("MULTIPLY", self, other)

    def __rmul__(self, other) -> t.Any:
        return _eval_operation("MULTIPLY", other, self)

    def __truediv__(self, other) -> t.Any:
        return _eval_operation("DIVIDE", self, other)

    def __rtruediv__(self, other) -> t.Any:
        return _eval_operation("DIVIDE", other, self)

    def __mod__(self, other) -> t.Any:
        return _eval_operation("MODULO", self, other)


class AriphmeticScalarMixin(Scalar, _AriphmeticMixin): ...


class AriphmeticContainerMixin(Container, _AriphmeticMixin): ...


class _ComparisonMixin:
    def __lt__(self, other) -> t.Any:
        return _eval_operation("LESS_THAN", self, other)

    def __le__(self, other) -> t.Any:
        return _eval_operation("LESS_EQUAL", self, other)

    def __gt__(self, other) -> t.Any:
        return _eval_operation("GREATER_THAN", self, other)

    def __ge__(self, other) -> t.Any:
        return _eval_operation("GREATER_EQUAL", self, other)

    def eq(self, other) -> t.Any:
        return _eval_operation("EQUALS", self, other)

    def ne(self, other) -> t.Any:
        return _eval_operation("NOT_EQUALS", self, other)

    def and_(self, other) -> t.Any:
        return _eval_operation("AND", self, other)

    def or_(self, other) -> t.Any:
        return _eval_operation("OR", self, other)

    def not_(self) -> t.Any:
        return _eval_operation("NOT", self)

    def like(self, pattern: t.Any) -> t.Any:
        return _eval_operation("LIKE", self, pattern)

    def nil(self) -> t.Any:
        return _eval_operation("NIL_Q", self)


class ComparisonScalarMixin(Scalar, _ComparisonMixin): ...


class ComparisonContainerMixin(Container, _ComparisonMixin): ...


class SortContainerMixin(Container):
    def asc(self) -> t.Any:
        return _eval_operation("ASC", self)

    def desc(self) -> t.Any:
        return _eval_operation("DESC", self)

    def iasc(self) -> t.Any:
        return _eval_operation("IASC", self)

    def idesc(self) -> t.Any:
        return _eval_operation("IDESC", self)

    def rank(self) -> t.Any:
        return _eval_operation("RANK", self)

    def xrank(self, i: int) -> t.Any:
        return _eval_operation("XRANK", self, i)

    def negate(self) -> t.Any:
        return _eval_operation("NEGATE", self)


class IterableContainerMixin(Container):
    def reverse(self) -> t.Any:
        return _eval_operation("REVERSE", self)


class _AggMixin:
    def ceil(self) -> t.Any:
        return _eval_operation("CEIL", self)

    def floor(self) -> t.Any:
        return _eval_operation("FLOOR", self)

    def round(self) -> t.Any:
        return _eval_operation("ROUND", self)

    def xbar(self, i: int) -> t.Any:
        return _eval_operation("XBAR", self, i)


class AggScalarMixin(_AggMixin, Scalar): ...


class AggContainerMixin(_AggMixin, Container):
    def sum(self) -> t.Any:
        return _eval_operation("SUM", self)

    def average(self) -> t.Any:
        return _eval_operation("AVG", self)

    def median(self) -> t.Any:
        return _eval_operation("MEDIAN", self)

    def deviation(self) -> t.Any:
        return _eval_operation("DEVIATION", self)

    def min(self) -> t.Any:
        return _eval_operation("MIN", self)

    def max(self) -> t.Any:
        return _eval_operation("MAX", self)


class ElementAccessContainerMixin(Container):
    def first(self) -> t.Any:
        return _eval_operation("FIRST", self)

    def last(self) -> t.Any:
        return _eval_operation("LAST", self)

    def take(self, i: int) -> t.Any:
        return _eval_operation("TAKE", self, i)

    def at(self, index: t.Any) -> t.Any:
        return _eval_operation("AT", self, index)


class SetOperationContainerMixin(Container):
    def except_(self, other: t.Any) -> t.Any:
        return _eval_operation("EXCEPT", self, other)

    def union(self, other: t.Any) -> t.Any:
        return _eval_operation("UNION", self, other)

    def sect(self, other: t.Any) -> t.Any:
        return _eval_operation("SECT", self, other)


class SearchContainerMixin(Container):
    def in_(self, other: t.Any) -> t.Any:
        return _eval_operation("IN", other, self)

    def find(self, value: t.Any) -> t.Any:
        return _eval_operation("FIND", self, value)

    def filter(self, mask: t.Any) -> t.Any:
        return _eval_operation("FILTER", self, mask)

    def within(self, range_: t.Any) -> t.Any:
        return _eval_operation("WITHIN", self, range_)


class FunctionalContainerMixin(Container):
    def map(self, fn: t.Any) -> t.Any:
        return _eval_operation("MAP", fn, self)

    def pmap(self, fn: t.Any) -> t.Any:
        return _eval_operation("PMAP", fn, self)

    def fold(self, fn: t.Any) -> t.Any:
        return _eval_operation("FOLD", fn, self)

    def apply(self, fn: t.Any, *others: t.Any) -> t.Any:
        return _eval_operation("APPLY", fn, self, *others)


class _MappableMixin:
    def key(self) -> t.Any:
        return _eval_operation("KEY", self)

    def value(self) -> t.Any:
        return _eval_operation("VALUE", self)


class MappableScalarMixin(_MappableMixin, Scalar): ...


class MappableContainerMixin(_MappableMixin, Container): ...


ValueAccessContainerMixin = ElementAccessContainerMixin  # backward compatibility
