import pytest

from rayforce import types as t


@pytest.mark.parametrize("value,expected", [("1", "1"), ("A", "A"), (" ", " ")])
def test_c8(value, expected):
    assert t.C8(value).value == expected


# --- C8: multi-character input (silently takes first character) ---


@pytest.mark.parametrize(
    "value,expected",
    [
        ("AB", "A"),
        ("hello", "h"),
        ("99", "9"),
    ],
)
def test_c8_multi_character_takes_first(value, expected):
    """C library silently takes only the first byte of multi-character strings."""
    assert t.C8(value).value == expected


# --- C8: empty string produces null byte ---


def test_c8_empty_string():
    assert t.C8("").value == "\x00"


# --- C8: multi-byte unicode characters raise UnicodeDecodeError ---


@pytest.mark.parametrize(
    "value",
    [
        "\u00f1",  # n-tilde (2 bytes in UTF-8)
        "\u20ac",  # euro sign (3 bytes in UTF-8)
        "\U0001f389",  # party popper emoji (4 bytes in UTF-8)
    ],
)
def test_c8_multibyte_unicode_raises(value):
    """C8 stores a single byte; multi-byte UTF-8 characters cannot be decoded from 1 byte."""
    with pytest.raises(UnicodeDecodeError):
        t.C8(value).value
