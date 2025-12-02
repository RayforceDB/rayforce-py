from rayforce import Table


def test_order_by():
    table = Table(
        columns=["id", "name", "age"],
        values=[
            ["001", "002", "003", "004"],
            ["alice", "bob", "charlie", "dana"],
            [29, 34, 41, 38],
        ],
    )

    result = table.xdesc("age")
    values = result.values()
    assert (
        values[2][0].value
        > values[2][1].value
        > values[2][2].value
        > values[2][3].value
    )

    result = table.xasc("age")
    values = result.values()
    assert (
        values[2][3].value
        > values[2][2].value
        > values[2][1].value
        > values[2][0].value
    )
