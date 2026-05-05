"""Comprehensive tests for the rayforce error class hierarchy."""

from __future__ import annotations

import pytest

from rayforce import errors

# ── All error classes inherit from RayforceError ────────────────────────────


@pytest.mark.parametrize(
    "cls",
    [
        errors.RayforceArityError,
        errors.RayforceConversionError,
        errors.RayforceDomainError,
        errors.RayforceEvaluationError,
        errors.RayforceIndexError,
        errors.RayforceInitError,
        errors.RayforceLengthError,
        errors.RayforceLimitError,
        errors.RayforceNYIError,
        errors.RayforceOSError,
        errors.RayforceOkError,
        errors.RayforceParseError,
        errors.RayforcePartedTableError,
        errors.RayforceQueryCompilationError,
        errors.RayforceTCPError,
        errors.RayforceThreadError,
        errors.RayforceTypeError,
        errors.RayforceTypeRegistryError,
        errors.RayforceUserError,
        errors.RayforceValueError,
        errors.RayforceWSError,
    ],
)
def test_error_inherits_from_rayforce_error(cls):
    assert issubclass(cls, errors.RayforceError)


# ── All error classes are subclasses of Exception ──────────────────────────


@pytest.mark.parametrize(
    "cls",
    [
        errors.RayforceArityError,
        errors.RayforceConversionError,
        errors.RayforceDomainError,
        errors.RayforceError,
        errors.RayforceEvaluationError,
        errors.RayforceIndexError,
        errors.RayforceInitError,
        errors.RayforceLengthError,
        errors.RayforceLimitError,
        errors.RayforceNYIError,
        errors.RayforceOSError,
        errors.RayforceOkError,
        errors.RayforceParseError,
        errors.RayforcePartedTableError,
        errors.RayforceQueryCompilationError,
        errors.RayforceTCPError,
        errors.RayforceThreadError,
        errors.RayforceTypeError,
        errors.RayforceTypeRegistryError,
        errors.RayforceUserError,
        errors.RayforceValueError,
        errors.RayforceWSError,
    ],
)
def test_error_is_exception(cls):
    assert issubclass(cls, Exception)


# ── Errors can be raised and caught ─────────────────────────────────────────


@pytest.mark.parametrize(
    "cls, msg",
    [
        (errors.RayforceArityError, "test arity"),
        (errors.RayforceConversionError, "test conversion"),
        (errors.RayforceDomainError, "test domain"),
        (errors.RayforceEvaluationError, "test eval"),
        (errors.RayforceIndexError, "test index"),
        (errors.RayforceInitError, "test init"),
        (errors.RayforceLengthError, "test length"),
        (errors.RayforceTypeError, "test type"),
        (errors.RayforceValueError, "test value"),
        (errors.RayforceUserError, "test user"),
    ],
)
def test_error_raise_and_catch(cls, msg):
    with pytest.raises(cls) as exc_info:
        raise cls(msg)
    assert msg in str(exc_info.value)


@pytest.mark.parametrize(
    "cls",
    [
        errors.RayforceArityError,
        errors.RayforceConversionError,
        errors.RayforceDomainError,
        errors.RayforceTypeError,
    ],
)
def test_error_caught_as_rayforce_error(cls):
    with pytest.raises(errors.RayforceError):
        raise cls("test")


@pytest.mark.parametrize(
    "cls",
    [errors.RayforceArityError, errors.RayforceTypeError, errors.RayforceValueError],
)
def test_error_caught_as_exception(cls):
    with pytest.raises(Exception):
        raise cls("test")


# ── Error code mapping ──────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "code, expected_cls",
    [
        ("ok", errors.RayforceOkError),
        ("type", errors.RayforceTypeError),
        ("arity", errors.RayforceArityError),
        ("length", errors.RayforceLengthError),
        ("domain", errors.RayforceDomainError),
        ("index", errors.RayforceIndexError),
        ("value", errors.RayforceValueError),
        ("limit", errors.RayforceLimitError),
        ("os", errors.RayforceOSError),
        ("parse", errors.RayforceParseError),
        ("nyi", errors.RayforceNYIError),
    ],
)
def test_core_exc_code_mapping(code, expected_cls):
    assert errors.CORE_EXC_CODE_MAPPING[code] is expected_cls


# ── Plugin-specific errors ──────────────────────────────────────────────────


def test_plugin_errors_module_imports():
    from rayforce.plugins import errors as plugin_errors

    assert hasattr(plugin_errors, "KDBConnectionError")
    assert hasattr(plugin_errors, "KDBConnectionAlreadyClosedError")


def test_kdb_errors_inherit_from_rayforce_error():
    from rayforce.plugins import errors as plugin_errors

    assert issubclass(plugin_errors.KDBConnectionError, errors.RayforceError)
    assert issubclass(plugin_errors.KDBConnectionAlreadyClosedError, errors.RayforceError)
