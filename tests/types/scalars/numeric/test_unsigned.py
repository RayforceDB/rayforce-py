import pytest
from rayforce import types as t


def test_u8():
    assert t.U8(0).value == 0
    assert t.U8(100).value == 100
    assert t.U8(255).value == 255
    assert t.U8(42.7).value == 42


def test_u8_out_of_range():
    with pytest.raises((t.RayInitException, OverflowError)):
        t.U8(256)
    with pytest.raises((t.RayInitException, OverflowError)):
        t.U8(-1)
