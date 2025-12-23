import pytest
from rayforce import types as t


def test_i16():
    assert t.I16(0).value == 0
    assert t.I16(100).value == 100
    assert t.I16(-100).value == -100


def test_i32():
    assert t.I32(0).value == 0
    assert t.I32(1000).value == 1000
    assert t.I32(-1000).value == -1000


def test_i64():
    assert t.I64(0).value == 0
    assert t.I64(1000000).value == 1000000
    assert t.I64(-1000000).value == -1000000
    assert t.I64(42).value == 42
    assert t.I64(2147483647).value == 2147483647
    assert t.I64(-2147483648).value == -2147483648
