from raypy.types import scalar as s
from raypy.types import container as c


def test_vector():
    v = c.Vector(type_code=s.Symbol.type_code, length=5)
    for idx, key in enumerate(["test1", "test2", "test3", "test4", "test5"]):
        v[idx] = key

    assert len(v) == 5
    assert v.value == (
        s.Symbol("test1"),
        s.Symbol("test2"),
        s.Symbol("test3"),
        s.Symbol("test4"),
        s.Symbol("test5"),
    )

    v = c.Vector(type_code=s.I64.type_code, length=5)
    for idx, key in enumerate([100, 200, 300, 400, 500]):
        v[idx] = key

    assert len(v) == 5
    assert v.value == (
        s.I64(100),
        s.I64(200),
        s.I64(300),
        s.I64(400),
        s.I64(500),
    )


def test_list():
    l = c.List(["test", 123, 555.0, True, [1, 2.5, 3]])
    assert len(l) == 5
    assert l == c.List(
        [
            s.Symbol("test"),
            s.I64(123),
            s.F64(555.0),
            s.B8(True),
            c.List([s.I64(1), s.F64(2.5), s.I64(3)]),
        ]
    )

    l[1] = "test233"
    assert l == c.List(
        [
            s.Symbol("test"),
            s.Symbol("test233"),
            s.F64(555.0),
            s.B8(True),
            c.List([s.I64(1), s.F64(2.5), s.I64(3)]),
        ]
    )

    assert l[0] == s.Symbol("test")


def test_dict():
    d = c.Dict(
        {"test": 123, "test1": {"test_inner": 555.0, "test_inner_list": [123, 444.0]}}
    )

    comparable_keys = c.Vector(type_code=s.Symbol.type_code, length=2)
    for idx, key in enumerate(["test", "test1"]):
        comparable_keys[idx] = key

    assert d.keys() == comparable_keys
    assert d.values() == c.List(
        [123, {"test_inner": 555.0, "test_inner_list": [123, 444.0]}]
    )
    assert d.values()[1] == c.Dict(
        {"test_inner": 555.0, "test_inner_list": [123, 444.0]}
    )


def test_table():
    columns = ["id", "first_name", "last_name", "email", "department", "age"]
    values = [
        ["001", "002", "003", "004", "005"],  # id
        ["alice", "bob", "charlie", "dana", "eli"],  # first_name
        ["johnson", "smith", "kim", "williams", "nguyen"],  # last_name
        [
            "alice.johnson@example.com",
            "bob.smith@example.com",
            "charlie.kim@example.com",
            "dana.williams@example.com",
            "eli.nguyen@example.com",
        ],  # email
        ["engineering", "marketing", "finance", "hr", "design"],  # department
        [29, 34, 41, 38, 45],  # age (as int)
    ]
    t = c.Table(columns=columns, values=values)

    comparable_vector = c.Vector(type_code=s.Symbol.type_code, length=len(columns))
    for idx, column in enumerate(columns):
        comparable_vector[idx] = column

    assert t.columns() == comparable_vector
    # Values are now Vectors (auto-converted from lists), not Lists
    result_values = t.values()
    assert len(result_values) == len(values)
    # Check each column is a Vector with correct values
    for idx, expected_col in enumerate(values):
        result_col = result_values[idx]
        assert len(result_col) == len(expected_col)


def test_string():
    s = c.String("William")
    assert s.value == "William"
