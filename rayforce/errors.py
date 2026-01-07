from __future__ import annotations

from functools import wraps
import typing as t

from rayforce import _rayforce_c as r

if t.TYPE_CHECKING:
    from rayforce import Dict


class RayforceError(Exception):
    @classmethod
    def serialize(cls, error: Dict) -> t.Self:
        raise cls(f"{error}")


class RayforceInitError(RayforceError): ...


class RayforceQueryCompilationError(RayforceError): ...


class RayforceTypeRegistryError(RayforceError): ...


class RayforceEvaluationError(RayforceError): ...


class RayforceConversionError(RayforceError): ...


class RayforcePartedTableError(RayforceError): ...


class RayforceTCPError(RayforceError): ...


class RayforceWSError(RayforceError): ...


class RayforceThreadError(RayforceError): ...


class RayforceOkError(RayforceError):
    """Core - EC_OK"""


class RayforceTypeError(RayforceError):
    """Core - EC_TYPE"""

    @classmethod
    def serialize(cls, error: Dict) -> t.Self:
        raise cls(f"expected: {error['expected']}, got: {error['got']}")


class RayforceArityError(RayforceError):
    """Core - EC_ARITY"""

    @classmethod
    def serialize(cls, error: Dict) -> t.Self:
        raise cls(f"expected: {error['expected']}, got: {error['got']}")


class RayforceLengthError(RayforceError):
    """Core - EC_LENGTH"""

    @classmethod
    def serialize(cls, error: Dict) -> t.Self:
        raise cls(f"need: {error['need']}, given: {error['have']}")


class RayforceDomainError(RayforceError):
    """Core - EC_DOMAIN"""


class RayforceIndexError(RayforceError):
    """Core - EC_INDEX"""

    @classmethod
    def serialize(cls, error: Dict) -> t.Self:
        raise cls(f"index: {error['index']}, bound: {error['bound']}")


class RayforceValueError(RayforceError):
    """Core - EC_VALUE"""

    @classmethod
    def serialize(cls, error: Dict) -> t.Self:
        if "name" in error:
            raise cls(f"name: {error['name']}")
        raise cls(f"{error}")


class RayforceLimitError(RayforceError):
    """Core - EC_LIMIT"""

    @classmethod
    def serialize(cls, error: Dict) -> t.Self:
        if "limit" in error:
            raise cls(f"limit: {error['limit']}")
        raise cls(f"{error}")


class RayforceOSError(RayforceError):
    """Core - EC_OS"""

    @classmethod
    def serialize(cls, error: Dict) -> t.Self:
        if "message" in error:
            raise cls(f"message: {error['message']}")
        raise cls(f"{error}")


class RayforceParseError(RayforceError):
    """Core - EC_PARSE"""


class RayforceNYIError(RayforceError):
    """Core - EC_NYI"""


class RayforceUserError(RayforceError):
    """Core - EC_USER"""


CORE_EXC_CODE_MAPPING: dict[str, type[RayforceError]] = {
    "ok": RayforceOkError,
    "type": RayforceTypeError,
    "arity": RayforceArityError,
    "length": RayforceLengthError,
    "domain": RayforceDomainError,
    "index": RayforceIndexError,
    "value": RayforceValueError,
    "limit": RayforceLimitError,
    "os": RayforceOSError,
    "parse": RayforceParseError,
    "nyi": RayforceNYIError,
}


def error_handler(func: t.Callable) -> t.Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        from rayforce.ffi import FFI

        result = func(*args, **kwargs)
        if isinstance(result, r.RayObject) and FFI.get_obj_type(result) == r.TYPE_ERR:
            from rayforce import Dict

            error = Dict(ptr=FFI.get_error_obj(result))
            raise CORE_EXC_CODE_MAPPING.get(error["code"].value, RayforceUserError).serialize(error)
        return result

    return wrapper
