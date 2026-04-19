import pytest

from rayforce import B8, I64, Column, Symbol, Table, Vector
from tests.helpers.assertions import assert_column_values, assert_table_shape

_CATEGORY_1 = pytest.mark.xfail(
    reason="GAPS.md Category 1 — DAG compiler rejects WHERE predicates / column refs (missing RAY_ATTR_NAME); see Task L8",
    strict=False,
)


@_CATEGORY_1
@pytest.mark.parametrize("is_inplace", [True, False])
def test_update_single_row(is_inplace, make_table):
    data = {
        "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
        "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
        "age": Vector(items=[29, 34, 41], ray_type=I64),
    }

    if is_inplace:
        result = Table(data).update(age=100).where(Column("id") == "001").execute()
    else:
        name, _ = make_table(data)
        result = Table(name).update(age=100).where(Column("id") == "001").execute()

    assert_table_shape(result, rows=3, cols=3)
    assert_column_values(result, "id", ["001", "002", "003"])
    assert_column_values(result, "name", ["alice", "bob", "charlie"])
    assert_column_values(result, "age", [100, 34, 41])


@_CATEGORY_1
def test_update_multiple_rows(make_table):
    name, _ = make_table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "dept": Vector(items=["eng", "eng", "marketing"], ray_type=Symbol),
            "salary": Vector(items=[100000, 120000, 90000], ray_type=I64),
        }
    )

    result = Table(name).update(salary=150000).where(Column("dept") == "eng").execute()

    assert_table_shape(result, rows=3, cols=3)
    assert_column_values(result, "id", ["001", "002", "003"])
    assert_column_values(result, "dept", ["eng", "eng", "marketing"])
    assert_column_values(result, "salary", [150000, 150000, 90000])


@pytest.mark.parametrize("is_inplace", [True, False])
def test_update_all_rows(is_inplace, make_table):
    data = {
        "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
        "status": Vector(items=["active", "active", "inactive"], ray_type=Symbol),
        "score": Vector(items=[10, 20, 30], ray_type=I64),
    }

    if is_inplace:
        result = Table(data).update(score=0).execute()
    else:
        name, _ = make_table(data)
        result = Table(name).update(score=0).execute()

    assert_table_shape(result, rows=3, cols=3)
    assert_column_values(result, "id", ["001", "002", "003"])
    assert_column_values(result, "status", ["active", "active", "inactive"])
    assert_column_values(result, "score", [0, 0, 0])


@_CATEGORY_1
def test_update_multiple_columns(make_table):
    name, _ = make_table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
            "salary": Vector(items=[50000, 60000], ray_type=I64),
        }
    )

    result = Table(name).update(age=30, salary=55000).where(Column("id") == "001").execute()

    assert_table_shape(result, rows=2, cols=4)
    assert_column_values(result, "id", ["001", "002"])
    assert_column_values(result, "name", ["alice", "bob"])
    assert_column_values(result, "age", [30, 34])
    assert_column_values(result, "salary", [55000, 60000])


@_CATEGORY_1
def test_update_with_comparison_condition(make_table):
    name, _ = make_table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "age": Vector(items=[25, 30, 35], ray_type=I64),
            "active": Vector(items=[True, False, True], ray_type=B8),
        }
    )

    result = Table(name).update(age=99).where(Column("age") > 30).execute()

    assert_column_values(result, "age", [25, 30, 99])


@_CATEGORY_1
def test_update_with_complex_condition(make_table):
    name, _ = make_table(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "dept": Vector(items=["eng", "eng", "marketing", "eng"], ray_type=Symbol),
            "salary": Vector(items=[100000, 120000, 90000, 110000], ray_type=I64),
        }
    )

    result = (
        Table(name)
        .update(salary=150000)
        .where((Column("dept") == "eng") & (Column("salary") < 115000))
        .execute()
    )

    assert_column_values(result, "salary", [150000, 120000, 90000, 150000])


@_CATEGORY_1
def test_update_no_matching_rows(make_table):
    name, _ = make_table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "status": Vector(items=["active", "active"], ray_type=Symbol),
        }
    )

    result = (
        Table(name)
        .update(status="inactive")
        .where(Column("id") == "999")  # No matching row
        .execute()
    )

    assert_column_values(result, "status", ["active", "active"])


@_CATEGORY_1
def test_update_with_column_expression():
    """UPDATE using a column expression (age = age + 1)."""
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41], ray_type=I64),
        },
    )

    result = table.update(age=Column("age") + 1).execute()

    assert_table_shape(result, rows=3, cols=2)
    assert_column_values(result, "age", [30, 35, 42])
    assert_column_values(result, "id", ["001", "002", "003"])


@_CATEGORY_1
def test_update_all_rows_with_expression():
    """UPDATE all rows without WHERE using a column expression (salary doubled)."""
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "salary": Vector(items=[100000, 120000, 90000], ray_type=I64),
        },
    )

    result = table.update(salary=Column("salary") * 2).execute()

    assert_table_shape(result, rows=3, cols=2)
    assert_column_values(result, "salary", [200000, 240000, 180000])
