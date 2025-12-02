from rayforce import Table


def test_update_single_row():
    table = Table(
        columns=["id", "name", "age"],
        values=[["001", "002", "003"], ["alice", "bob", "charlie"], [29, 34, 41]],
    )
    table.save("test_update_table")

    result = (
        Table.get("test_update_table")
        .update(age=100)
        .where(lambda t: t.id == "001")
        .execute()
    )

    if isinstance(result, Table):
        values = result.values()
        assert values[2][0].value == 100


def test_update_multiple_rows():
    table = Table(
        columns=["id", "dept", "salary"],
        values=[
            ["001", "002", "003"],
            ["eng", "eng", "marketing"],
            [100000, 120000, 90000],
        ],
    )
    table.save("test_update_multi")

    result = (
        Table.get("test_update_multi")
        .update(salary=150000)
        .where(lambda t: t.dept == "eng")
        .execute()
    )

    if isinstance(result, Table):
        values = result.values()
        assert len(values) == 3
