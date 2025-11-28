from rayforce import types as t


def test_b8():
    assert t.B8(True).value == True
    assert t.B8(False).value == False
    assert t.B8(0).value == False
    assert t.B8(1).value == True
    assert t.B8("True").value == True
    assert t.B8("False").value == True
