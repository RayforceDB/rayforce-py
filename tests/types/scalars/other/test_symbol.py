from raypy import types as t


def test_symbol():
    assert t.Symbol("Test").value == "Test"
    assert t.Symbol("123").value == "123"
    assert t.Symbol("").value == ""
