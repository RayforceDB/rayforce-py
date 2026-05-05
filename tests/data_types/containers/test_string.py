import pytest

from rayforce import errors
from rayforce import types as t


@pytest.mark.parametrize("value,expected_len", [("Hello", 5), ("World", 5)])
def test_string(value, expected_len):
    s = t.String(value)
    assert s.to_python() == value
    assert len(s) == expected_len


class TestStringEmpty:
    def test_empty_string_creation(self):
        s = t.String("")
        assert s.to_python() == ""
        assert len(s) == 0

    def test_empty_string_iteration(self):
        s = t.String("")
        assert list(s) == []


class TestStringSpecialCharacters:
    def test_string_with_digits(self):
        s = t.String("abc123")
        assert s.to_python() == "abc123"
        assert len(s) == 6

    def test_string_with_punctuation(self):
        s = t.String("hello, world!")
        assert s.to_python() == "hello, world!"

    def test_string_with_newline(self):
        s = t.String("line1\nline2")
        assert s.to_python() == "line1\nline2"

    def test_string_with_tab(self):
        s = t.String("col1\tcol2")
        assert s.to_python() == "col1\tcol2"


class TestStringLong:
    def test_long_string(self):
        long_val = "a" * 10_000
        s = t.String(long_val)
        assert len(s) == 10_000
        assert s.to_python() == long_val

    def test_moderately_long_string(self):
        val = "hello " * 500
        s = t.String(val)
        assert s.to_python() == val


class TestStringIndexing:
    def test_index_first_char(self):
        s = t.String("Hello")
        assert s[0].value == "H"

    def test_index_last_char(self):
        s = t.String("Hello")
        assert s[4].value == "o"

    def test_negative_index(self):
        s = t.String("Hello")
        assert s[-1].value == "o"

    def test_negative_index_first(self):
        s = t.String("Hello")
        assert s[-5].value == "H"

    def test_index_out_of_range(self):
        s = t.String("Hi")
        with pytest.raises(errors.RayforceIndexError, match="out of range"):
            s[2]

    def test_iteration_chars(self):
        s = t.String("abc")
        chars = [c.value for c in s]
        assert chars == ["a", "b", "c"]


class TestStringEquality:
    def test_equal_strings(self):
        s1 = t.String("hello")
        s2 = t.String("hello")
        assert s1 == s2

    def test_unequal_strings(self):
        s1 = t.String("hello")
        s2 = t.String("world")
        assert s1 != s2
