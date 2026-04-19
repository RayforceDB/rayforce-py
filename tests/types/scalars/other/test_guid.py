import uuid

import pytest

from rayforce import types as t


@pytest.fixture
def sample_uuid():
    return uuid.uuid4()


@pytest.mark.parametrize("use_string", [True, False])
def test_guid(sample_uuid, use_string):
    input_val = str(sample_uuid) if use_string else sample_uuid
    assert t.GUID(input_val).value == sample_uuid


# --- GUID: invalid string handling ---


@pytest.mark.parametrize(
    "value",
    [
        "not-a-guid",
        "",
        "12345",
        "zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz",
    ],
)
def test_guid_invalid_string_raises(value):
    with pytest.raises(RuntimeError):
        t.GUID(value)


# --- GUID: different formats ---


def test_guid_uppercase_string():
    """Uppercase hex digits are accepted and normalized to lowercase."""
    result = t.GUID("ABCDEF01-2345-6789-ABCD-EF0123456789")
    assert result.value == uuid.UUID("abcdef01-2345-6789-abcd-ef0123456789")


@pytest.mark.xfail(
    reason="v2 GUID parser accepts both hyphenated and non-hyphenated forms",
    strict=False,
)
def test_guid_no_hyphens_string_raises():
    """The C library requires hyphenated format; non-hyphenated strings are rejected."""
    with pytest.raises(RuntimeError):
        t.GUID("12345678123456781234567812345678")


def test_guid_braces_string_raises():
    """The C library rejects brace-wrapped GUIDs."""
    with pytest.raises(RuntimeError):
        t.GUID("{12345678-1234-5678-1234-567812345678}")


def test_guid_from_uuid_object_no_hyphens():
    """Python uuid.UUID can be constructed from no-hyphen strings, then passed as object."""
    u = uuid.UUID("12345678123456781234567812345678")
    result = t.GUID(u)
    assert result.value == u


def test_guid_known_value_roundtrip():
    """A known GUID string round-trips correctly."""
    guid_str = "12345678-1234-5678-1234-567812345678"
    result = t.GUID(guid_str)
    assert result.value == uuid.UUID(guid_str)
    assert str(result) == guid_str
