import pytest

from rayforce import F64, I64, Column, Symbol, Table, Vector
from tests.helpers.assertions import (
    assert_column_sorted,
    assert_column_values,
    assert_columns,
    assert_contains_columns,
    assert_table_shape,
)


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_desc(is_inplace, make_table):
    data = {
        "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
        "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
        "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
    }

    if is_inplace:
        result = Table(data).order_by(Column("age"), desc=True).execute()
    else:
        name, _ = make_table(data)
        result = Table(name).order_by(Column("age"), desc=True).execute()

    assert_column_values(result, "age", [41, 38, 34, 29])
    assert_column_sorted(result, "age", desc=True)
    assert_column_values(result, "id", ["003", "004", "002", "001"])
    assert_column_values(result, "name", ["charlie", "dana", "bob", "alice"])


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_asc(is_inplace, make_table):
    data = {
        "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
        "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
        "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
    }

    if is_inplace:
        result = Table(data).order_by(Column("age")).execute()
    else:
        name, _ = make_table(data)
        result = Table(name).order_by(Column("age")).execute()

    assert_column_values(result, "age", [29, 34, 38, 41])
    assert_column_sorted(result, "age")
    assert_column_values(result, "id", ["001", "002", "004", "003"])
    assert_column_values(result, "name", ["alice", "bob", "dana", "charlie"])


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_multiple_columns(is_inplace, make_table):
    """Test ordering by multiple columns."""
    data = {
        "dept": Vector(items=["eng", "eng", "marketing", "marketing"], ray_type=Symbol),
        "salary": Vector(items=[100000, 120000, 90000, 110000], ray_type=I64),
        "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
    }

    if is_inplace:
        result = Table(data).order_by(Column("dept"), Column("salary")).execute()
    else:
        name, _ = make_table(data)
        result = Table(name).order_by(Column("dept"), Column("salary")).execute()

    assert_column_values(result, "dept", ["eng", "eng", "marketing", "marketing"])
    assert_column_values(result, "salary", [100000, 120000, 90000, 110000])
    assert_column_values(result, "name", ["alice", "bob", "charlie", "dana"])


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_string_column(is_inplace, make_table):
    """Test ordering by string column."""
    data = {
        "id": Vector(items=["003", "001", "004", "002"], ray_type=Symbol),
        "name": Vector(items=["charlie", "alice", "dana", "bob"], ray_type=Symbol),
    }

    if is_inplace:
        result = Table(data).order_by(Column("name")).execute()
    else:
        name, _ = make_table(data)
        result = Table(name).order_by(Column("name")).execute()

    assert_column_values(result, "name", ["alice", "bob", "charlie", "dana"])
    assert_column_values(result, "id", ["001", "002", "003", "004"])


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_preserves_all_rows(is_inplace, make_table):
    """Test that ordering preserves all rows and columns."""
    data = {
        "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
        "value": Vector(items=[3, 1, 2], ray_type=I64),
    }

    if is_inplace:
        result = Table(data).order_by(Column("value")).execute()
    else:
        name, _ = make_table(data)
        result = Table(name).order_by(Column("value")).execute()

    assert_table_shape(result, rows=3, cols=2)
    assert_contains_columns(result, ["id", "value"])
    assert_column_values(result, "value", [1, 2, 3])


def test_order_by_chained_with_select():
    """Test that order_by can be chained with select."""
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "name": Vector(items=["charlie", "alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[30, 25, 28], ray_type=I64),
        },
    )

    result = table.select("name", "age").order_by("age").execute()

    assert_columns(result, ["name", "age"])
    assert_column_values(result, "age", [25, 28, 30])


def test_order_by_chained_with_where():
    """Test that order_by can be chained with where."""
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "age": Vector(items=[25, 30, 35, 28], ray_type=I64),
        },
    )

    result = table.where(Column("age") > 26).order_by("age").execute()

    assert_table_shape(result, rows=3, cols=2)
    assert_column_values(result, "age", [28, 30, 35])


def test_order_by_with_null_values():
    """ORDER BY on a column that contains NULL values; NULLs sort to the beginning (0Nj = INT_MIN)."""
    left = Table(
        {
            "key": Vector(items=["a", "b", "c"], ray_type=Symbol),
            "val": Vector(items=[30, 10, 20], ray_type=I64),
        },
    )
    right = Table(
        {
            "key": Vector(items=["a", "b"], ray_type=Symbol),
            "score": Vector(items=[5, 3], ray_type=I64),
        },
    )
    joined = left.left_join(right, "key").execute()

    result = joined.order_by(Column("score")).execute()

    assert_table_shape(result, rows=3, cols=3)
    # Nulls (0Nj = INT_MIN) sort to the beginning in ascending order
    row_first = result.at_row(0)
    assert row_first["score"] == None  # noqa: E711  (Rayforce Null == None is True)
    assert row_first["key"] == "c"
    # Non-null rows are sorted ascending
    assert result.at_row(1)["score"] == 3
    assert result.at_row(2)["score"] == 5


def test_order_by_multiple_columns_desc():
    """ORDER BY multiple columns with desc=True sorts all columns descending."""
    table = Table(
        {
            "dept": Vector(items=["eng", "eng", "marketing", "marketing"], ray_type=Symbol),
            "salary": Vector(items=[120000, 100000, 90000, 110000], ray_type=I64),
            "name": Vector(items=["bob", "alice", "charlie", "dana"], ray_type=Symbol),
        },
    )

    result = table.order_by(Column("dept"), Column("salary"), desc=True).execute()

    assert_table_shape(result, rows=4, cols=3)
    # Descending: marketing before eng, higher salary first within dept
    assert_column_values(result, "dept", ["marketing", "marketing", "eng", "eng"])
    assert_column_values(result, "salary", [110000, 90000, 120000, 100000])


def test_order_by_stability():
    """ORDER BY preserves original relative order for rows with equal sort keys."""
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "score": Vector(items=[10, 20, 10, 20], ray_type=I64),
        },
    )

    result = table.order_by(Column("score")).execute()

    assert_table_shape(result, rows=4, cols=2)
    assert_column_sorted(result, "score")
    # Within score=10 group, original order (alice, charlie) is preserved
    assert_column_values(result, "name", ["alice", "charlie", "bob", "dana"])
    assert_column_values(result, "score", [10, 10, 20, 20])


def test_order_by_float_column():
    """ORDER BY on an F64 column."""
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "price": Vector(items=[3.14, 1.59, 2.65, 0.99], ray_type=F64),
        },
    )

    result = table.order_by(Column("price")).execute()

    assert_column_sorted(result, "price")
    assert_column_values(result, "id", ["004", "002", "003", "001"])
    assert_column_values(result, "price", [0.99, 1.59, 2.65, 3.14])
