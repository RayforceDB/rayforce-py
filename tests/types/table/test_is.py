import pytest

from rayforce import B8, I64, Column, List, Symbol, Table, Vector
from tests.helpers.assertions import (
    assert_column_set,
    assert_column_values,
    assert_table_shape,
)

# v2 query engine has open bugs around `is` filter projection.
# Tracked in UPGRADE.md Phase 7 known gaps.
pytestmark = pytest.mark.xfail(
    reason="v2 query engine filter projection; see UPGRADE.md Phase 7",
    strict=False,
)


def test_is_true_filters_true_rows():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "active": Vector(items=[True, False, True], ray_type=B8),
        },
    )

    result = table.select("name").where(Column("active").is_(True)).execute()

    assert_table_shape(result, rows=2, cols=1)
    assert_column_set(result, "name", {"alice", "charlie"})


def test_is_true_filters_true_rows_list():
    table = Table(
        {
            "name": List(["alice", "bob", "charlie"]),
            "active": List([True, False, True]),
        },
    )

    result = table.select("name").where(Column("active").is_(True)).execute()

    assert_table_shape(result, rows=2, cols=1)
    assert_column_set(result, "name", {"alice", "charlie"})


def test_is_false_filters_false_rows_list():
    table = Table(
        {
            "name": List(["alice", "bob", "charlie"]),
            "active": List([True, False, True]),
        },
    )

    result = table.select("name").where(Column("active").is_(False)).execute()

    assert_table_shape(result, rows=1, cols=1)
    assert_column_values(result, "name", ["bob"])


def test_is_false_filters_false_rows():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "active": Vector(items=[True, False, True], ray_type=B8),
        },
    )

    result = table.select("name").where(Column("active").is_(False)).execute()

    assert_table_shape(result, rows=1, cols=1)
    assert_column_values(result, "name", ["bob"])


def test_is_true_with_all_true():
    table = Table(
        {
            "id": Vector(items=[1, 2, 3], ray_type=I64),
            "flag": Vector(items=[True, True, True], ray_type=B8),
        },
    )

    result = table.select("id").where(Column("flag").is_(True)).execute()

    assert_table_shape(result, rows=3, cols=1)


def test_is_false_with_all_false():
    table = Table(
        {
            "id": Vector(items=[1, 2, 3], ray_type=I64),
            "flag": Vector(items=[False, False, False], ray_type=B8),
        },
    )

    result = table.select("id").where(Column("flag").is_(False)).execute()

    assert_table_shape(result, rows=3, cols=1)


def test_is_combined_with_other_conditions():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "active": Vector(items=[True, False, True, True], ray_type=B8),
            "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
        },
    )

    result = (
        table.select("name").where(Column("active").is_(True)).where(Column("age") >= 35).execute()
    )

    assert_table_shape(result, rows=2, cols=1)
    assert_column_set(result, "name", {"charlie", "dana"})


def test_is_with_group_by():
    table = Table(
        {
            "dept": Vector(items=["eng", "eng", "hr", "hr"], ray_type=Symbol),
            "active": Vector(items=[True, False, True, True], ray_type=B8),
            "salary": Vector(items=[100, 200, 150, 250], ray_type=I64),
        },
    )

    result = (
        table.select(
            active_total=Column("salary").where(Column("active").is_(True)).sum(),
        )
        .by("dept")
        .execute()
    )

    rows = {result.at_row(i)["dept"]: result.at_row(i) for i in range(len(result))}
    assert rows["eng"]["active_total"] == 100
    assert rows["hr"]["active_total"] == 400


def test_is_on_expression():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "score": Vector(items=[80, 50, 90], ray_type=I64),
        },
    )

    result = table.select("name").where((Column("score") > 60).is_(True)).execute()

    assert_table_shape(result, rows=2, cols=1)
    assert_column_set(result, "name", {"alice", "charlie"})
