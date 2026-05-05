import pytest

from rayforce import I64, Symbol, Table, Vector
from tests.helpers.assertions import assert_column_values, assert_table_shape


@pytest.mark.parametrize("is_inplace", [True, False])
def test_upsert_single_row_kwargs(is_inplace, make_table):
    data = {
        "id": Vector(items=["001", "002"], ray_type=Symbol),
        "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        "age": Vector(items=[29, 34], ray_type=I64),
    }

    if is_inplace:
        result = Table(data).upsert(id="001", name="alice_updated", age=30, key_columns=1).execute()
    else:
        name, _ = make_table(data)
        result = Table(name).upsert(id="001", name="alice_updated", age=30, key_columns=1).execute()

    assert_table_shape(result, rows=2, cols=3)
    assert_column_values(result, "name", ["alice_updated", "bob"])
    assert_column_values(result, "age", [30, 34])


@pytest.mark.parametrize("is_inplace", [True, False])
def test_upsert_single_row_args(is_inplace, make_table):
    data = {
        "id": Vector(items=["001", "002"], ray_type=Symbol),
        "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        "age": Vector(items=[29, 34], ray_type=I64),
    }

    if is_inplace:
        result = Table(data).upsert("001", "alice_updated", 30, key_columns=1).execute()
    else:
        name, _ = make_table(data)
        result = Table(name).upsert("001", "alice_updated", 30, key_columns=1).execute()

    assert_table_shape(result, rows=2, cols=3)
    assert_column_values(result, "name", ["alice_updated", "bob"])
    assert_column_values(result, "age", [30, 34])


@pytest.mark.parametrize("is_inplace", [True, False])
def test_upsert_multiple_rows_kwargs(is_inplace, make_table):
    data = {
        "id": Vector(items=["001", "002"], ray_type=Symbol),
        "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        "age": Vector(items=[29, 34], ray_type=I64),
    }

    if is_inplace:
        result = (
            Table(data)
            .upsert(
                id=["001", "003"],
                name=["alice_new", "charlie"],
                age=[30, 41],
                key_columns=1,
            )
            .execute()
        )
    else:
        name, _ = make_table(data)
        result = (
            Table(name)
            .upsert(
                id=["001", "003"],
                name=["alice_new", "charlie"],
                age=[30, 41],
                key_columns=1,
            )
            .execute()
        )

    assert len(result) >= 2
    assert_column_values(result, "name", ["alice_new", "bob", "charlie"])
    assert_column_values(result, "age", [30, 34, 41])


@pytest.mark.parametrize("is_inplace", [True, False])
def test_upsert_multiple_rows_args(is_inplace, make_table):
    data = {
        "id": Vector(items=["001", "002"], ray_type=Symbol),
        "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        "age": Vector(items=[29, 34], ray_type=I64),
    }

    if is_inplace:
        result = (
            Table(data)
            .upsert(
                ["001", "003"],
                ["alice_new", "charlie"],
                [30, 41],
                key_columns=1,
            )
            .execute()
        )
    else:
        name, _ = make_table(data)
        result = (
            Table(name)
            .upsert(
                ["001", "003"],
                ["alice_new", "charlie"],
                [30, 41],
                key_columns=1,
            )
            .execute()
        )

    assert len(result) >= 2
    assert_column_values(result, "name", ["alice_new", "bob", "charlie"])
    assert_column_values(result, "age", [30, 34, 41])


def test_upsert_to_empty_table():
    table = Table(
        {
            "id": Vector(items=[], ray_type=Symbol),
            "name": Vector(items=[], ray_type=Symbol),
            "age": Vector(items=[], ray_type=I64),
        },
    )

    result = table.upsert(
        ["001", "003"],
        ["alice", "charlie"],
        [30, 41],
        key_columns=1,
    ).execute()

    assert len(result) >= 2
    assert_column_values(result, "name", ["alice", "charlie"])
    assert_column_values(result, "age", [30, 41])


def test_upsert_with_multiple_key_columns():
    """UPSERT using key_columns=2 — composite key matching."""
    table = Table(
        {
            "dept": Vector(items=["eng", "eng", "hr"], ray_type=Symbol),
            "level": Vector(items=["senior", "junior", "senior"], ray_type=Symbol),
            "salary": Vector(items=[150000, 100000, 120000], ray_type=I64),
        },
    )

    result = table.upsert(
        dept=["eng", "marketing"],
        level=["senior", "junior"],
        salary=[160000, 90000],
        key_columns=2,
    ).execute()

    assert_table_shape(result, rows=4, cols=3)
    # eng/senior updated from 150000 -> 160000; marketing/junior is new
    assert_column_values(result, "dept", ["eng", "eng", "hr", "marketing"])
    assert_column_values(result, "level", ["senior", "junior", "senior", "junior"])
    assert_column_values(result, "salary", [160000, 100000, 120000, 90000])


def test_upsert_all_new_rows():
    """UPSERT where none of the keys match — all rows are inserted."""
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        },
    )

    result = table.upsert(
        id=["003", "004"],
        name=["charlie", "dana"],
        age=[41, 38],
        key_columns=1,
    ).execute()

    assert_table_shape(result, rows=4, cols=3)
    assert_column_values(result, "id", ["001", "002", "003", "004"])
    assert_column_values(result, "name", ["alice", "bob", "charlie", "dana"])
    assert_column_values(result, "age", [29, 34, 41, 38])


def test_upsert_all_existing_rows():
    """UPSERT where every key matches — all rows are updated, none inserted."""
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41], ray_type=I64),
        },
    )

    result = table.upsert(
        id=["001", "002", "003"],
        name=["alice_v2", "bob_v2", "charlie_v2"],
        age=[30, 35, 42],
        key_columns=1,
    ).execute()

    assert_table_shape(result, rows=3, cols=3)
    assert_column_values(result, "id", ["001", "002", "003"])
    assert_column_values(result, "name", ["alice_v2", "bob_v2", "charlie_v2"])
    assert_column_values(result, "age", [30, 35, 42])
