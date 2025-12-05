from rayforce import types as t


def test_list():
    l = t.List(["test", 123, 555.0, True])
    assert len(l) == 4
    assert l[0].value == "test"
    assert l[1].value == 123
    assert l[2].value == 555.0
    assert l[3].value == True

    l.append(999)
    assert len(l) == 5
    assert l[4].value == 999

    l[0] = "this is test"
    assert l[0] == t.Symbol("this is test")
