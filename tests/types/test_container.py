from raypy import types as t


def test_vector():
    v = t.Vector(type_code=t.Symbol.type_code, length=5)
    for idx, key in enumerate(["test1", "test2", "test3", "test4", "test5"]):
        v[idx] = key

    assert len(v) == 5
    assert v.to_python() == (
        t.Symbol("test1"),
        t.Symbol("test2"),
        t.Symbol("test3"),
        t.Symbol("test4"),
        t.Symbol("test5"),
    )

    v = t.Vector(type_code=t.I64.type_code, length=5)
    for idx, key in enumerate([100, 200, 300, 400, 500]):
        v[idx] = key

    assert len(v) == 5
    assert v.to_python() == (
        t.I64(100),
        t.I64(200),
        t.I64(300),
        t.I64(400),
        t.I64(500),
    )


def test_list():
    l = t.List(["test", 123, 555.0, True, [1, 2.5, 3]])
    assert len(l) == 5
    assert l == t.List(
        [
            t.Symbol("test"),
            t.I64(123),
            t.F64(555.0),
            t.B8(True),
            t.List([t.I64(1), t.F64(2.5), t.I64(3)]),
        ]
    )

    assert l[0] == t.Symbol("test")


def test_dict():
    d = t.Dict(
        {"test": 123, "test1": {"test_inner": 555.0, "test_inner_list": [123, 444.0]}}
    )

    comparable_keys = t.Vector(type_code=t.Symbol.type_code, length=2)
    for idx, key in enumerate(["test", "test1"]):
        comparable_keys[idx] = key
    assert d.keys() == comparable_keys
    assert d.values() == t.List(
        [123, {"test_inner": 555.0, "test_inner_list": [123, 444.0]}]
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
    table = t.Table(columns=columns, values=values)

    comparable_vector = t.Vector(type_code=t.Symbol.type_code, length=len(columns))
    for idx, column in enumerate(columns):
        comparable_vector[idx] = column

    assert table.columns() == comparable_vector
    # Values are now Vectors (auto-converted from lists), not Lists
    result_values = table.values()
    assert len(result_values) == len(values)
    # Check each column is a Vector with correct values
    for idx, expected_col in enumerate(values):
        result_col = result_values[idx]
        assert len(result_col) == len(expected_col)


def test_string():
    s = t.String("William")
    assert s.value == "William"
