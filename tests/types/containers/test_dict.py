from rayforce import types as t


def test_dict():
    d = t.Dict({"key1": 123, "key2": "value2"})
    assert len(d) == 2

    keys = d.keys()
    assert len(keys) == 2
    assert keys[0].value == "key1"
    assert keys[1].value == "key2"

    values = d.values()
    assert len(values) == 2
    assert values[0].value == 123
    assert values[1].value == "value2"

    d["key1"] = 222

    assert d["key1"] == 222
