import pytest
from rayforce import types as t


def test_c8():
    assert t.C8("1").value == "1"
    assert t.C8("A").value == "A"
    assert t.C8(" ").value == " "


def test_c8_out_of_range():
    with pytest.raises(t.RayInitException):
        t.C8("123")
    with pytest.raises(t.RayInitException):
        t.C8("")
