import typing as t


class CAPIError(Exception):
    pass


def c_api_exception_handler(func: t.Callable) -> t.Callable:
    """
    Decorator which handles all errors which might arise during C API function call
    """

    def wrapper(*args, **kwargs) -> t.Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise CAPIError(f"Error during {func.__name__} C API call") from e

    return wrapper
