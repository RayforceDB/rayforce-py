from raypy import types as t


def test_string():
    s = t.String("Hello")
    assert s.value == "Hello"
    assert len(s) == 5

    s2 = t.String("World")
    assert s2.value == "World"
    assert len(s2) == 5
