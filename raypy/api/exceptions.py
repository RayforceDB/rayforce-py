import typing as t
from typing import TypeVar, ParamSpec

P = ParamSpec("P")
T = TypeVar("T")


class CAPIError(Exception):
    pass


def c_api_exception_handler(func: t.Callable[P, T]) -> t.Callable[P, T]:
    """
    Decorator which handles all errors which might arise during C API function call
    """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise CAPIError(f"Error during {func.__name__} C API call") from e

    return wrapper
