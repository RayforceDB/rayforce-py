import pytest

from rayforce import I64, Symbol, Table, Vector


@pytest.mark.parametrize("is_inplace", [True, False])
def test_insert_single_row_kwargs(is_inplace):
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        },
    )

    if is_inplace:
        result = table.insert(id="003", name="charlie", age=41).execute()
    else:
        table.save("test_insert_table")
        result = Table("test_insert_table").insert(id="003", name="charlie", age=41).execute()

    assert isinstance(result, Table)

    values = result.values()
    assert len(values[0]) == 3
    assert values[0][2].value == "003"
    assert values[1][2].value == "charlie"
    assert values[2][2].value == 41


@pytest.mark.parametrize("is_inplace", [True, False])
def test_insert_single_row_args(is_inplace):
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        },
    )

    if is_inplace:
        result = table.insert("003", "charlie", 41).execute()
    else:
        table.save("test_insert_table")
        result = Table("test_insert_table").insert("003", "charlie", 41).execute()

    assert isinstance(result, Table)

    values = result.values()
    assert len(values[0]) == 3
    assert values[0][2].value == "003"
    assert values[1][2].value == "charlie"
    assert values[2][2].value == 41


@pytest.mark.parametrize("is_inplace", [True, False])
def test_insert_multiple_rows_kwargs(is_inplace):
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        },
    )

    if is_inplace:
        result = table.insert(id=["003", "004"], name=["charlie", "megan"], age=[41, 30]).execute()
    else:
        table.save("test_insert_table")
        result = (
            Table("test_insert_table")
            .insert(id=["003", "004"], name=["charlie", "megan"], age=[41, 30])
            .execute()
        )

    assert isinstance(result, Table)

    values = result.values()
    assert len(values[0]) == 4
    assert values[0][2].value == "003"
    assert values[1][2].value == "charlie"
    assert values[2][2].value == 41

    assert values[0][3].value == "004"
    assert values[1][3].value == "megan"
    assert values[2][3].value == 30


@pytest.mark.parametrize("is_inplace", [True, False])
def test_insert_multiple_rows_args(is_inplace):
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        },
    )

    if is_inplace:
        result = table.insert(["003", "004"], ["charlie", "megan"], [41, 30]).execute()
    else:
        table.save("test_insert_table")
        result = (
            Table("test_insert_table")
            .insert(["003", "004"], ["charlie", "megan"], [41, 30])
            .execute()
        )

    assert isinstance(result, Table)

    values = result.values()
    assert len(values[0]) == 4
    assert values[0][2].value == "003"
    assert values[1][2].value == "charlie"
    assert values[2][2].value == 41

    assert values[0][3].value == "004"
    assert values[1][3].value == "megan"
    assert values[2][3].value == 30
