from rayforce import types as t


def test_string():
    s = t.String("Hello")
    assert s.to_python() == "Hello"
    assert len(s) == 5

    s2 = t.String("World")
    assert s2.to_python() == "World"
    assert len(s2) == 5
