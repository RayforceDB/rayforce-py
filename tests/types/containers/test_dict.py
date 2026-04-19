import pytest

from rayforce import types as t


def test_dict_creation():
    d = t.Dict({"key1": 123, "key2": "value2"})
    assert len(d) == 2


def test_dict_keys_values():
    d = t.Dict({"key1": 123, "key2": "value2"})

    keys = d.keys()
    assert len(keys) == 2
    assert keys[0].value == "key1"
    assert keys[1].value == "key2"

    values = d.values()
    assert len(values) == 2
    assert values[0].value == 123
    assert values[1].value == "value2"


@pytest.mark.xfail(
    reason="Dict key-based __setitem__ needs rework for v2; see UPGRADE.md Phase 7",
    strict=False,
)
def test_dict_assignment():
    d = t.Dict({"key1": 123, "key2": "value2"})
    d["key1"] = 222
    assert d["key1"] == 222


class TestDictEmpty:
    def test_empty_dict_creation(self):
        d = t.Dict({})
        assert len(d) == 0

    def test_empty_dict_keys(self):
        d = t.Dict({})
        keys = d.keys()
        assert len(keys) == 0

    def test_empty_dict_values(self):
        d = t.Dict({})
        values = d.values()
        assert len(values) == 0

    def test_empty_dict_iteration(self):
        d = t.Dict({})
        assert list(d) == []


class TestDictNonExistentKey:
    def test_missing_key_returns_null(self):
        d = t.Dict({"key1": 123})
        result = d["nonexistent"]
        assert result == t.Null


class TestDictIteration:
    def test_iter_yields_keys(self):
        d = t.Dict({"a": 1, "b": 2, "c": 3})
        keys = [k.value for k in d]
        assert keys == ["a", "b", "c"]

    def test_items_yields_key_value_pairs(self):
        d = t.Dict({"x": 10, "y": 20})
        pairs = [(k.value, v.value) for k, v in d.items()]
        assert pairs == [("x", 10), ("y", 20)]

    def test_to_python(self):
        d = t.Dict({"k1": 100, "k2": "hello"})
        result = d.to_python()
        assert isinstance(result, dict)
        assert result == {"k1": 100, "k2": "hello"}


class TestDictNestedValues:
    def test_dict_with_list_value(self):
        d = t.Dict({"nums": [1, 2, 3], "name": "test"})
        assert d["name"] == "test"

    def test_dict_with_mixed_value_types(self):
        d = t.Dict({"int_val": 42, "str_val": "hello", "float_val": 3.14})
        assert d["int_val"] == 42
        assert d["str_val"] == "hello"
        assert d["float_val"] == 3.14


class TestDictSpecialKeys:
    def test_key_with_spaces(self):
        d = t.Dict({"key with spaces": 1})
        assert d["key with spaces"] == 1

    def test_key_with_numbers(self):
        d = t.Dict({"key123": 42})
        assert d["key123"] == 42

    def test_single_char_key(self):
        d = t.Dict({"x": 99})
        assert d["x"] == 99
