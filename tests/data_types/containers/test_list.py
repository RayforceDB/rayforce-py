import pytest

from rayforce import errors
from rayforce import types as t


def test_list_creation():
    l = t.List(["test", 123, 555.0, True])
    assert len(l) == 4
    assert l[0].value == "test"
    assert l[1].value == 123
    assert l[2].value == 555.0
    assert l[3].value is True


def test_list_append():
    l = t.List(["test", 123, 555.0, True])
    l.append(999)
    assert len(l) == 5
    assert l[4].value == 999


def test_list_assignment():
    l = t.List(["test", 123, 555.0, True])
    l[0] = "this is test"
    assert l[0] == t.Symbol("this is test")


class TestListEmpty:
    def test_empty_list_creation(self):
        l = t.List([])
        assert len(l) == 0

    def test_empty_list_iteration(self):
        l = t.List([])
        assert list(l) == []

    def test_empty_list_bool_is_false(self):
        l = t.List([])
        assert not l

    def test_empty_list_append_then_access(self):
        l = t.List([])
        l.append(42)
        assert len(l) == 1
        assert l[0].value == 42


class TestListNegativeIndexing:
    def test_negative_index_last(self):
        l = t.List([10, 20, 30])
        assert l[-1].value == 30

    def test_negative_index_first(self):
        l = t.List([10, 20, 30])
        assert l[-3].value == 10

    def test_negative_index_out_of_range(self):
        l = t.List([10, 20, 30])
        with pytest.raises(errors.RayforceIndexError, match="out of range"):
            l[-4]


class TestListOutOfBounds:
    def test_positive_index_out_of_bounds(self):
        l = t.List([10, 20, 30])
        with pytest.raises(errors.RayforceIndexError, match="out of range"):
            l[3]

    def test_large_positive_index(self):
        l = t.List([10])
        with pytest.raises(errors.RayforceIndexError, match="out of range"):
            l[100]


class TestListIteration:
    def test_for_loop(self):
        l = t.List(["a", "b", "c"])
        values = [item.value for item in l]
        assert values == ["a", "b", "c"]

    def test_to_python(self):
        l = t.List([1, "two", 3.0])
        result = l.to_python()
        assert isinstance(result, list)
        assert len(result) == 3


class TestListAppendTypes:
    def test_append_string(self):
        l = t.List([1])
        l.append("hello")
        assert l[1].value == "hello"

    def test_append_float(self):
        l = t.List([1])
        l.append(3.14)
        assert l[1].value == 3.14

    def test_append_bool(self):
        l = t.List([1])
        l.append(True)
        assert len(l) == 2
        assert l[1].value is True

    def test_append_none(self):
        l = t.List([1])
        l.append(None)
        assert len(l) == 2
