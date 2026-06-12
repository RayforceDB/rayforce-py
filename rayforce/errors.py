from __future__ import annotations

from functools import wraps
import typing as t

from rayforce import _rayforce_c as r

if t.TYPE_CHECKING:
    from rayforce import Dict


class RayforceError(Exception):
    @classmethod
    def serialize(cls, error: Dict) -> t.NoReturn:
        # Core error objects carry exactly two fields: `code` and `message`
        # (see capi build_err_dict). Earlier per-subclass overrides referenced
        # fields like `expected`/`got` that the core never populates, yielding
        # "expected: Null" messages — so decode uniformly off `message`.
        code = error["code"]
        message = error["message"]
        code_s = getattr(code, "value", code)
        msg_s = getattr(message, "value", message)
        raise cls(f"{code_s}: {msg_s}" if msg_s else str(code_s))


class RayforceInitError(RayforceError): ...


class RayforceQueryCompilationError(RayforceError): ...


class RayforceTypeRegistryError(RayforceError): ...


class RayforceEvaluationError(RayforceError): ...


class RayforceConversionError(RayforceError): ...


class RayforcePartedTableError(RayforceError): ...


class RayforceTCPError(RayforceError): ...


class RayforceThreadError(RayforceError): ...


class RayforceOkError(RayforceError):
    """Core - EC_OK"""


class RayforceTypeError(RayforceError):
    """Core - EC_TYPE"""


class RayforceArityError(RayforceError):
    """Core - EC_ARITY"""


class RayforceLengthError(RayforceError):
    """Core - EC_LENGTH"""


class RayforceDomainError(RayforceError):
    """Core - EC_DOMAIN"""


class RayforceIndexError(RayforceError):
    """Core - EC_INDEX"""


class RayforceValueError(RayforceError):
    """Core - EC_VALUE"""


class RayforceLimitError(RayforceError):
    """Core - EC_LIMIT"""


class RayforceOSError(RayforceError):
    """Core - EC_OS"""


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
