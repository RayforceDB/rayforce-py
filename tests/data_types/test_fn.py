import pytest

from rayforce import I64, Column, Fn, Symbol, Table, Vector
from tests.helpers.assertions import (
    assert_column_values,
    assert_contains_columns,
    assert_table_shape,
)

_RECURSIVE_SELF_IN_DAG = pytest.mark.xfail(
    reason="recursive `self` not bound during DAG β-reduction; see "
    "docs/core_bugs/recursive_self_in_dag.md",
    strict=False,
)


def test_fn_direct_call_scalar():
    square = Fn("(fn [x] (* x x))")
    assert square(5) == 25
    assert square(10) == 100


def test_fn_direct_call_multiple_args():
    add = Fn("(fn [x y] (+ x y))")
    assert add(5, 3) == 8
    assert add(10, 20) == 30


def test_fn_fibonacci_direct_call():
    fib = Fn("(fn [x] (if (< x 2) 1 (+ (self (- x 1)) (self (- x 2)))))")

    assert fib(0) == 1
    assert fib(1) == 1
    assert fib(2) == 2
    assert fib(3) == 3
    assert fib(4) == 5


def test_fn_apply_to_column():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "value": Vector(items=[2, 3, 4], ray_type=I64),
        },
    )

    square = Fn("(fn [x] (* x x))")
    result = table.select("id", squared_value=square.apply(Column("value"))).execute()

    assert_contains_columns(result, ["id", "squared_value"])
    assert_column_values(result, "squared_value", [4, 9, 16])


def test_fn_apply_with_aggregation():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "value": Vector(items=[2, 3, 4, 5], ray_type=I64),
        },
    )

    square = Fn("(fn [x] (* x x))")
    result = table.select(
        sum_of_squares=square.apply(Column("value")).sum(),
        avg_of_squares=square.apply(Column("value")).mean(),
        max_of_squares=square.apply(Column("value")).max(),
    ).execute()

    assert_contains_columns(result, ["sum_of_squares", "avg_of_squares", "max_of_squares"])
    assert_column_values(result, "sum_of_squares", [54])
    assert_column_values(result, "avg_of_squares", [13.5])
    assert_column_values(result, "max_of_squares", [25])


def test_fn_apply_with_group_by():
    table = Table(
        {
            "category": Vector(items=["A", "A", "B", "B"], ray_type=Symbol),
            "value": Vector(items=[2, 3, 4, 5], ray_type=I64),
        },
    )

    square = Fn("(fn [x] (* x x))")
    result = (
        table.select(sum_of_squares=square.apply(Column("value")).sum()).by("category").execute()
    )

    assert_contains_columns(result, ["category", "sum_of_squares"])
    assert_table_shape(result, rows=2, cols=2)

    # Group order is unspecified; verify the set of (category, sum) pairs.
    categories = [c.to_python() for c in result.values()[0]]
    sums = [v.value for v in result.values()[1]]
    assert dict(zip(categories, sums, strict=True)) == {"A": 13, "B": 41}


def test_fn_normalize_with_multiple_args():
    table = Table(
        {
            "value": Vector(items=[50, 75, 100], ray_type=I64),
            "min_val": Vector(items=[0, 0, 0], ray_type=I64),
            "max_val": Vector(items=[100, 100, 100], ray_type=I64),
        },
    )

    normalize = Fn("(fn [x min_val max_val] (/ (- x min_val) (- max_val min_val)))")
    result = table.select(
        "value",
        normalized=normalize.apply(Column("value"), Column("min_val"), Column("max_val")),
    ).execute()

    assert_contains_columns(result, ["value", "normalized"])
    assert_column_values(result, "normalized", [0.5, 0.75, 1.0])


@_RECURSIVE_SELF_IN_DAG
def test_fn_fibonacci_with_aggregation():
    table = Table(
        {
            "group": Vector(items=["A", "A", "B", "B"], ray_type=Symbol),
            "n": Vector(items=[0, 1, 2, 3], ray_type=I64),
        },
    )

    fib = Fn("(fn [x] (if (< x 2) 1 (+ (self (- x 1)) (self (- x 2)))))")
    result = (
        table.select(
            fib_sum=fib.apply(Column("n")).sum(),
            fib_max=fib.apply(Column("n")).max(),
            fib_count=fib.apply(Column("n")).count(),
        )
        .by("group")
        .execute()
    )

    assert_contains_columns(result, ["group", "fib_sum", "fib_max", "fib_count"])
    assert_table_shape(result, rows=2, cols=4)


def test_fn_complex_expression():
    table = Table(
        {
            "x": Vector(items=[2, 3, 4], ray_type=I64),
            "y": Vector(items=[3, 4, 5], ray_type=I64),
        },
    )

    sum_squares = Fn("(fn [x y] (+ (* x x) (* y y)))")
    result = table.select(
        "x",
        "y",
        sum_of_squares=sum_squares.apply(Column("x"), Column("y")),
    ).execute()

    assert_contains_columns(result, ["x", "y", "sum_of_squares"])
    assert_column_values(result, "sum_of_squares", [13, 25, 41])


def test_fn_conditional_lambda():
    table = Table(
        {
            "value": Vector(items=[-5, 0, 5, 10], ray_type=I64),
        },
    )

    abs_fn = Fn("(fn [x] (if (< x 0) (* -1 x) x))")
    result = table.select("value", abs_value=abs_fn.apply(Column("value"))).execute()

    assert_contains_columns(result, ["value", "abs_value"])
    assert_column_values(result, "abs_value", [5, 0, 5, 10])


def test_fn_with_where_clause():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "value": Vector(items=[2, 3, 4, 5], ray_type=I64),
        },
    )

    square = Fn("(fn [x] (* x x))")
    result = (
        table.select("id", squared_value=square.apply(Column("value")))
        .where(Column("value") > 3)
        .execute()
    )

    assert_contains_columns(result, ["id", "squared_value"])
    assert_table_shape(result, rows=2, cols=2)
    assert_column_values(result, "squared_value", [16, 25])
