import pytest

from rayforce import I64, Symbol, Table, Vector, errors
from tests.helpers.assertions import assert_column_values, assert_table_shape

# Some insert tests depend on v2 select projection; see UPGRADE.md Phase 7.
pytestmark = pytest.mark.xfail(
    reason="v2 query engine insert; see UPGRADE.md Phase 7",
    strict=False,
)


@pytest.mark.parametrize("is_inplace", [True, False])
def test_insert_single_row_kwargs(is_inplace, make_table):
    data = {
        "id": Vector(items=["001", "002"], ray_type=Symbol),
        "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        "age": Vector(items=[29, 34], ray_type=I64),
    }

    if is_inplace:
        result = Table(data).insert(id="003", name="charlie", age=41).execute()
    else:
        name, _ = make_table(data)
        result = Table(name).insert(id="003", name="charlie", age=41).execute()

    assert_table_shape(result, rows=3, cols=3)
    assert_column_values(result, "id", ["001", "002", "003"])
    assert_column_values(result, "name", ["alice", "bob", "charlie"])
    assert_column_values(result, "age", [29, 34, 41])


@pytest.mark.parametrize("is_inplace", [True, False])
def test_insert_single_row_args(is_inplace, make_table):
    data = {
        "id": Vector(items=["001", "002"], ray_type=Symbol),
        "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        "age": Vector(items=[29, 34], ray_type=I64),
    }

    if is_inplace:
        result = Table(data).insert("003", "charlie", 41).execute()
    else:
        name, _ = make_table(data)
        result = Table(name).insert("003", "charlie", 41).execute()

    assert_table_shape(result, rows=3, cols=3)
    assert_column_values(result, "id", ["001", "002", "003"])
    assert_column_values(result, "name", ["alice", "bob", "charlie"])
    assert_column_values(result, "age", [29, 34, 41])


@pytest.mark.parametrize("is_inplace", [True, False])
def test_insert_multiple_rows_kwargs(is_inplace, make_table):
    data = {
        "id": Vector(items=["001", "002"], ray_type=Symbol),
        "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        "age": Vector(items=[29, 34], ray_type=I64),
    }

    if is_inplace:
        result = (
            Table(data).insert(id=["003", "004"], name=["charlie", "megan"], age=[41, 30]).execute()
        )
    else:
        name, _ = make_table(data)
        result = (
            Table(name).insert(id=["003", "004"], name=["charlie", "megan"], age=[41, 30]).execute()
        )

    assert_table_shape(result, rows=4, cols=3)
    assert_column_values(result, "id", ["001", "002", "003", "004"])
    assert_column_values(result, "name", ["alice", "bob", "charlie", "megan"])
    assert_column_values(result, "age", [29, 34, 41, 30])


@pytest.mark.parametrize("is_inplace", [True, False])
def test_insert_multiple_rows_args(is_inplace, make_table):
    data = {
        "id": Vector(items=["001", "002"], ray_type=Symbol),
        "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        "age": Vector(items=[29, 34], ray_type=I64),
    }

    if is_inplace:
        result = Table(data).insert(["003", "004"], ["charlie", "megan"], [41, 30]).execute()
    else:
        name, _ = make_table(data)
        result = Table(name).insert(["003", "004"], ["charlie", "megan"], [41, 30]).execute()

    assert_table_shape(result, rows=4, cols=3)
    assert_column_values(result, "id", ["001", "002", "003", "004"])
    assert_column_values(result, "name", ["alice", "bob", "charlie", "megan"])
    assert_column_values(result, "age", [29, 34, 41, 30])


def test_insert_with_type_mismatch():
    """Insert with a value whose type does not match the column type raises RayforceTypeError."""
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        },
    )

    with pytest.raises(errors.RayforceTypeError):
        table.insert(id="003", age="not_a_number").execute()


def test_insert_into_empty_table():
    """Insert a row into a table that starts with zero rows."""
    table = Table(
        {
            "id": Vector(items=[], ray_type=Symbol),
            "name": Vector(items=[], ray_type=Symbol),
            "age": Vector(items=[], ray_type=I64),
        },
    )

    result = table.insert(id="001", name="alice", age=29).execute()

    assert_table_shape(result, rows=1, cols=3)
    assert_column_values(result, "id", ["001"])
    assert_column_values(result, "name", ["alice"])
    assert_column_values(result, "age", [29])
