import pytest
from rayforce import Table, Vector, Symbol, I64


@pytest.mark.parametrize("is_inplace", [True, False])
def test_upsert_single_row_kwargs(is_inplace):
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        },
    )

    if is_inplace:
        result = table.upsert(id="001", name="alice_updated", age=30, match_by_first=1).execute()
    else:
        table.save("test_upsert_table")
        result = (
            Table.from_name("test_upsert_table")
            .upsert(id="001", name="alice_updated", age=30, match_by_first=1)
            .execute()
        )

    assert isinstance(result, Table)

    values = result.values()
    assert len(values[0]) == 2
    assert values[1][0].value == "alice_updated"
    assert values[2][0].value == 30


@pytest.mark.parametrize("is_inplace", [True, False])
def test_upsert_single_row_args(is_inplace):
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        },
    )

    if is_inplace:
        result = table.upsert("001", "alice_updated", 30, match_by_first=1).execute()
    else:
        table.save("test_upsert_table")
        result = (
            Table.from_name("test_upsert_table")
            .upsert("001", "alice_updated", 30, match_by_first=1)
            .execute()
        )

    assert isinstance(result, Table)

    values = result.values()
    assert len(values[0]) == 2
    assert values[1][0].value == "alice_updated"
    assert values[2][0].value == 30


@pytest.mark.parametrize("is_inplace", [True, False])
def test_upsert_multiple_rows_kwargs(is_inplace):
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        },
    )

    if is_inplace:
        result = table.upsert(
            id=["001", "003"],
            name=["alice_new", "charlie"],
            age=[30, 41],
            match_by_first=1,
        ).execute()
    else:
        table.save("test_upsert_multi")
        result = (
            Table.from_name("test_upsert_multi")
            .upsert(
                id=["001", "003"],
                name=["alice_new", "charlie"],
                age=[30, 41],
                match_by_first=1,
            )
            .execute()
        )

    assert isinstance(result, Table)

    values = result.values()
    assert len(values[0]) >= 2
    assert values[1][0].value == "alice_new"
    assert values[2][0].value == 30
    assert values[1][2].value == "charlie"
    assert values[2][2].value == 41


@pytest.mark.parametrize("is_inplace", [True, False])
def test_upsert_multiple_rows_args(is_inplace):
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        },
    )

    if is_inplace:
        result = table.upsert(
            ["001", "003"],
            ["alice_new", "charlie"],
            [30, 41],
            match_by_first=1,
        ).execute()
    else:
        table.save("test_upsert_multi")
        result = (
            Table.from_name("test_upsert_multi")
            .upsert(
                ["001", "003"],
                ["alice_new", "charlie"],
                [30, 41],
                match_by_first=1,
            )
            .execute()
        )

    assert isinstance(result, Table)

    values = result.values()
    assert len(values[0]) >= 2
    assert values[1][0].value == "alice_new"
    assert values[2][0].value == 30
    assert values[1][2].value == "charlie"
    assert values[2][2].value == 41
