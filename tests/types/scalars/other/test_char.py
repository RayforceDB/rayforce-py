from rayforce import types as t


def test_c8():
    assert t.C8("1").value == "1"
    assert t.C8("A").value == "A"
    assert t.C8(" ").value == " "
