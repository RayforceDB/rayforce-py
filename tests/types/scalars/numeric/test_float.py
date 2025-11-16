from raypy import types as t


def test_f64():
    assert t.F64(0).value == 0.0
    assert t.F64(123).value == 123.0
    assert t.F64(-123).value == -123.0
    assert t.F64(123.45).value == 123.45
    assert t.F64(-123.45).value == -123.45
    assert t.F64(42.7).value == 42.7
