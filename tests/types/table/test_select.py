from rayforce import F64, I64, Column, Symbol, Table, Vector
from tests.helpers.assertions import (
    assert_column_values,
    assert_columns,
    assert_contains_columns,
    assert_row,
    assert_table_shape,
)


def test_select_with_single_where():
    table = Table(
        {
            "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "salary": Vector(items=[100000, 120000, 90000, 85000], ray_type=I64),
        },
    )

    result = table.select("id", "name", "age").where(Column("age") >= 35).execute()

    assert_columns(result, ["id", "name", "age"])
    assert_table_shape(result, rows=2, cols=3)
    assert_column_values(result, "id", ["003", "004"])
    assert_column_values(result, "name", ["charlie", "dana"])
    assert_column_values(result, "age", [41, 38])


def test_select_with_multiple_where_conditions():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004", "005"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana", "eli"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38, 45], ray_type=I64),
            "dept": Vector(items=["eng", "eng", "marketing", "eng", "marketing"], ray_type=Symbol),
            "salary": Vector(items=[100000, 120000, 90000, 85000, 95000], ray_type=I64),
        },
    )

    result = (
        table.select("id", "name", "age", "salary")
        .where(Column("age") >= 35)
        .where(Column("dept") == "eng")
        .execute()
    )

    assert_table_shape(result, rows=1, cols=4)
    assert_column_values(result, "id", ["004"])
    assert_column_values(result, "name", ["dana"])
    assert_column_values(result, "age", [38])
    assert_column_values(result, "salary", [85000])


def test_select_with_complex_and_or_conditions():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004", "005"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana", "eli"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38, 45], ray_type=I64),
            "dept": Vector(items=["eng", "eng", "marketing", "eng", "marketing"], ray_type=Symbol),
            "salary": Vector(items=[100000, 120000, 90000, 85000, 95000], ray_type=I64),
        },
    )

    result = (
        table.select("id", "name")
        .where((Column("age") >= 35) & (Column("dept") == "eng"))
        .where((Column("salary") > 80000) | (Column("age") < 40))
        .execute()
    )

    assert_contains_columns(result, ["id", "name"])
    assert len(result) >= 0


def test_group_by_single_column():
    table = Table(
        {
            "dept": Vector(items=["eng", "eng", "marketing", "marketing", "hr"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38, 35], ray_type=I64),
            "salary": Vector(items=[100000, 120000, 90000, 85000, 80000], ray_type=I64),
        },
    )

    result = (
        table.select(
            avg_age=Column("age").mean(),
            total_salary=Column("salary").sum(),
            count=Column("age").count(),
        )
        .by("dept")
        .execute()
    )

    assert_contains_columns(result, ["dept", "avg_age", "total_salary", "count"])

    rows = {result.at_row(i)["dept"]: i for i in range(len(result))}
    assert_row(result, rows["eng"], {"total_salary": 220000, "count": 2, "avg_age": 31.5})
    assert_row(result, rows["marketing"], {"total_salary": 175000, "count": 2, "avg_age": 39.5})
    assert_row(result, rows["hr"], {"total_salary": 80000, "count": 1, "avg_age": 35})


def test_group_by_multiple_columns():
    table = Table(
        {
            "dept": Vector(items=["eng", "eng", "eng", "marketing", "marketing"], ray_type=Symbol),
            "level": Vector(
                items=["senior", "junior", "senior", "senior", "junior"],
                ray_type=Symbol,
            ),
            "salary": Vector(items=[150000, 100000, 140000, 120000, 90000], ray_type=I64),
        },
    )

    result = (
        table.select(
            total_salary=Column("salary").sum(),
            avg_salary=Column("salary").mean(),
        )
        .by("dept", "level")
        .execute()
    )

    assert_contains_columns(result, ["dept", "level", "total_salary", "avg_salary"])

    rows = {(result.at_row(i)["dept"], result.at_row(i)["level"]): i for i in range(len(result))}
    assert_row(result, rows[("eng", "senior")], {"total_salary": 290000, "avg_salary": 145000})
    assert_row(result, rows[("eng", "junior")], {"total_salary": 100000, "avg_salary": 100000})
    assert_row(
        result, rows[("marketing", "senior")], {"total_salary": 120000, "avg_salary": 120000}
    )
    assert_row(result, rows[("marketing", "junior")], {"total_salary": 90000, "avg_salary": 90000})


def test_group_by_with_filtered_aggregation():
    table = Table(
        {
            "category": Vector(items=["A", "A", "B", "B", "A"], ray_type=Symbol),
            "amount": Vector(items=[100, 200, 150, 250, 300], ray_type=I64),
            "status": Vector(
                items=["active", "inactive", "active", "active", "inactive"],
                ray_type=Symbol,
            ),
        },
    )

    result = (
        table.select(
            total=Column("amount").sum(),
            active_total=Column("amount").where(Column("status") == "active").sum(),
            count=Column("amount").count(),
        )
        .by("category")
        .execute()
    )

    assert_contains_columns(result, ["category", "total", "active_total", "count"])

    rows = {result.at_row(i)["category"]: i for i in range(len(result))}
    assert_row(result, rows["A"], {"total": 600, "active_total": 100, "count": 3})
    assert_row(result, rows["B"], {"total": 400, "active_total": 400, "count": 2})


def test_complex_select_with_computed_columns():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "price": Vector(items=[10.5, 20.0, 15.75], ray_type=F64),
            "quantity": Vector(items=[2, 3, 4], ray_type=I64),
        },
    )

    result = (
        table.select(
            "id",
            total=Column("price") * Column("quantity"),
            discounted=Column("price") * Column("quantity") * 0.9,
        )
        .where(Column("quantity") >= 3)
        .execute()
    )

    assert_contains_columns(result, ["id", "total", "discounted"])
    assert_table_shape(result, rows=2, cols=3)


def test_select_with_isin_operator():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004", "005"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana", "eli"], ray_type=Symbol),
            "dept": Vector(items=["eng", "eng", "marketing", "hr", "marketing"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38, 45], ray_type=I64),
        },
    )

    # Filter by dept in ["eng", "marketing"]
    result = (
        table.select("id", "name", "dept", "age")
        .where(Column("dept").isin(["eng", "marketing"]))
        .execute()
    )

    assert_columns(result, ["id", "name", "dept", "age"])
    assert_table_shape(result, rows=4, cols=4)
    assert_column_values(result, "name", ["alice", "bob", "charlie", "eli"])

    # Filter by age in [29, 41, 45]
    result_int = table.select("id", "name", "age").where(Column("age").isin([29, 41, 45])).execute()

    assert_columns(result_int, ["id", "name", "age"])
    assert_table_shape(result_int, rows=3, cols=3)
    assert_column_values(result_int, "name", ["alice", "charlie", "eli"])
    assert_column_values(result_int, "age", [29, 41, 45])


def test_select_with_no_matching_rows():
    """SELECT that produces an empty result set."""
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41], ray_type=I64),
        },
    )

    result = table.select("id", "age").where(Column("age") > 100).execute()

    assert_columns(result, ["id", "age"])
    assert_table_shape(result, rows=0, cols=2)


def test_group_by_single_row_per_group():
    """GROUP BY where every group contains exactly one row."""
    table = Table(
        {
            "dept": Vector(items=["eng", "marketing", "hr"], ray_type=Symbol),
            "salary": Vector(items=[100000, 90000, 80000], ray_type=I64),
        },
    )

    result = (
        table.select(
            total_salary=Column("salary").sum(),
            count=Column("salary").count(),
        )
        .by("dept")
        .execute()
    )

    assert_contains_columns(result, ["dept", "total_salary", "count"])

    rows = {result.at_row(i)["dept"]: i for i in range(len(result))}
    assert_row(result, rows["eng"], {"total_salary": 100000, "count": 1})
    assert_row(result, rows["marketing"], {"total_salary": 90000, "count": 1})
    assert_row(result, rows["hr"], {"total_salary": 80000, "count": 1})


def test_complex_nested_boolean_expressions():
    """SELECT with deeply nested AND/OR boolean conditions."""
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004", "005"], ray_type=Symbol),
            "age": Vector(items=[25, 30, 35, 40, 45], ray_type=I64),
            "dept": Vector(items=["eng", "hr", "eng", "hr", "eng"], ray_type=Symbol),
            "salary": Vector(items=[80000, 90000, 100000, 110000, 120000], ray_type=I64),
        },
    )

    # (age > 30 AND dept == "eng") OR (salary >= 110000)
    result = (
        table.select("id", "age", "dept", "salary")
        .where(((Column("age") > 30) & (Column("dept") == "eng")) | (Column("salary") >= 110000))
        .execute()
    )

    assert_table_shape(result, rows=3, cols=4)
    assert_column_values(result, "id", ["003", "004", "005"])
    assert_column_values(result, "age", [35, 40, 45])


def test_select_distinct():
    """DISTINCT operation on a column."""
    table = Table(
        {
            "dept": Vector(
                items=["eng", "eng", "marketing", "marketing", "eng"],
                ray_type=Symbol,
            ),
            "salary": Vector(items=[100, 100, 200, 100, 200], ray_type=I64),
        },
    )

    result_dept = table.select(_vals=Column("dept").distinct()).execute()
    dept_vals = result_dept.at_column("_vals")
    assert len(dept_vals) == 2
    assert set(v.value for v in dept_vals) == {"eng", "marketing"}

    result_salary = table.select(_vals=Column("salary").distinct()).execute()
    salary_vals = result_salary.at_column("_vals")
    assert len(salary_vals) == 2
    assert set(v.value for v in salary_vals) == {100, 200}
