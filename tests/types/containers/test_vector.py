from rayforce import types as t


def test_vector():
    v = t.Vector(ray_type=t.Symbol, length=3)
    v[0] = "test1"
    v[1] = "test2"
    v[2] = "test3"

    assert len(v) == 3
    assert v[0].value == "test1"
    assert v[1].value == "test2"
    assert v[2].value == "test3"

    v2 = t.Vector(ray_type=t.I64, items=[100, 200, 300])
    assert len(v2) == 3
    assert v2[0].value == 100
    assert v2[1].value == 200
    assert v2[2].value == 300
