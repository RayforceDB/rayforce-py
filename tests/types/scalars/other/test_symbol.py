import pytest

from rayforce import types as t


@pytest.mark.parametrize("value,expected", [("Test", "Test"), ("123", "123"), ("", "")])
def test_symbol(value, expected):
    assert t.Symbol(value).value == expected


# --- Symbol: special characters ---


@pytest.mark.parametrize(
    "value",
    [
        "@#$%",
        "hello world",
        "tab\there",
        "new\nline",
        "a/b/c",
        "key=value",
    ],
)
def test_symbol_special_characters(value):
    assert t.Symbol(value).value == value


# --- Symbol: unicode ---


@pytest.mark.parametrize(
    "value",
    [
        "caf\u00e9",
        "\u65e5\u672c\u8a9e",
        "\U0001f389",
    ],
)
def test_symbol_unicode(value):
    assert t.Symbol(value).value == value


# --- Symbol: very long strings ---


@pytest.mark.parametrize("length", [1_000, 10_000])
def test_symbol_long_string(length):
    value = "a" * length
    result = t.Symbol(value)
    assert result.value == value
    assert len(result.value) == length
