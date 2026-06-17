import pytest

from rayforce import I64, Column, List, Symbol, Table, Vector
from tests.helpers.assertions import (
    assert_column_values,
    assert_columns,
    assert_table_shape,
)


@pytest.fixture
def grouped_data():
    """Dataset whose `dept` grouping yields uneven group sizes (3 + 1)."""
    return {
        "dept": Vector(items=["eng", "eng", "marketing", "eng"], ray_type=Symbol),
        "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
        "salary": Vector(items=[100000, 120000, 90000, 85000], ray_type=I64),
    }


def test_ungroup_grouped_select(grouped_data):
    """Eager ungroup: run a grouped non-aggregating select, then flatten the
    nested LIST columns back to row form via Table.ungroup()."""
    grouped = (
        Table(grouped_data)
        .select(name=Column("name"), salary=Column("salary"))
        .by("dept")
        .execute()
    )

    # Grouped result has one row per dept with nested LIST cells.
    assert_table_shape(grouped, rows=2, cols=3)

    result = grouped.ungroup()

    assert_columns(result, ["dept", "name", "salary"])
    assert_table_shape(result, rows=4, cols=3)
    # eng group (3 rows) expands first, then marketing (1 row); atom `dept`
    # column is replicated per element.
    assert_column_values(result, "dept", ["eng", "eng", "eng", "marketing"])
    assert_column_values(result, "name", ["alice", "bob", "dana", "charlie"])
    assert_column_values(result, "salary", [100000, 120000, 85000, 90000])


def test_ungroup_deferred_query(grouped_data):
    """Deferred ungroup: t.select(...).by(...).ungroup().execute() produces the
    same flattened result as the eager path."""
    result = (
        Table(grouped_data)
        .select(name=Column("name"), salary=Column("salary"))
        .by("dept")
        .ungroup()
        .execute()
    )

    assert_columns(result, ["dept", "name", "salary"])
    assert_table_shape(result, rows=4, cols=3)
    assert_column_values(result, "dept", ["eng", "eng", "eng", "marketing"])
    assert_column_values(result, "name", ["alice", "bob", "dana", "charlie"])
    assert_column_values(result, "salary", [100000, 120000, 85000, 90000])


def test_ungroup_direct_list_column():
    """Ungroup a table whose LIST column was built directly (not via select):
    each list cell expands to one row, atom columns replicated per element."""
    table = Table(
        {
            "k": Vector(items=["x", "y"], ray_type=Symbol),
            "v": List(
                [
                    Vector(items=[1, 2], ray_type=I64),
                    Vector(items=[3], ray_type=I64),
                ]
            ),
        }
    )

    result = table.ungroup()

    assert_columns(result, ["k", "v"])
    assert_table_shape(result, rows=3, cols=2)
    assert_column_values(result, "k", ["x", "x", "y"])
    assert_column_values(result, "v", [1, 2, 3])


def test_ungroup_flat_table_is_noop():
    """A table with no nested LIST columns is returned unchanged."""
    table = Table({"a": Vector(items=[1, 2, 3], ray_type=I64)})

    result = table.ungroup()

    assert_columns(result, ["a"])
    assert_table_shape(result, rows=3, cols=1)
    assert_column_values(result, "a", [1, 2, 3])
