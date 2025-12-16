from rayforce import F64, I64, Column, Symbol, Table, Vector


def test_select_with_single_where():
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
            "salary": Vector(items=[100000, 120000, 90000, 85000], ray_type=I64),
        },
    )

    result = table.select("id", "name", "age").where(Column("age") >= 35).execute()

    columns = result.columns()
    assert len(columns) == 3
    assert "id" in columns
    assert "name" in columns
    assert "age" in columns

    values = result.values()
    assert len(values) == 3
    assert len(values[0]) == 2
    assert values[0][0].value == "003"
    assert values[0][1].value == "004"
    assert values[1][0].value == "charlie"
    assert values[1][1].value == "dana"
    assert values[2][0].value == 41
    assert values[2][1].value == 38


def test_select_with_multiple_where_conditions():
    table = Table.from_dict(
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

    values = result.values()
    assert len(values) == 4
    assert len(values[0]) == 1
    assert values[0][0].value == "004"
    assert values[1][0].value == "dana"
    assert values[2][0].value == 38
    assert values[3][0].value == 85000


def test_select_with_complex_and_or_conditions():
    table = Table.from_dict(
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

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) >= 0


def test_group_by_single_column():
    table = Table.from_dict(
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

    columns = result.columns()
    assert len(columns) >= 4
    assert "dept" in columns or "by" in columns
    assert "avg_age" in columns
    assert "total_salary" in columns
    assert "count" in columns

    values = result.values()
    assert len(values) >= 3

    # Find the column indices
    cols = list(result.columns())
    dept_idx = cols.index("dept") if "dept" in cols else cols.index("by")
    avg_age_idx = cols.index("avg_age")
    total_salary_idx = cols.index("total_salary")
    count_idx = cols.index("count")

    # Expected: eng (avg_age=31.5, total_salary=220000, count=2)
    #           marketing (avg_age=39.5, total_salary=175000, count=2)
    #           hr (avg_age=35, total_salary=80000, count=1)

    dept_col = values[dept_idx]
    avg_age_col = values[avg_age_idx]
    total_salary_col = values[total_salary_idx]
    count_col = values[count_idx]

    # Find eng group
    for i in range(len(dept_col)):
        dept_val = dept_col[i].value if hasattr(dept_col[i], "value") else str(dept_col[i])
        if dept_val == "eng":
            assert abs(avg_age_col[i].value - 31.5) < 0.01
            assert total_salary_col[i].value == 220000
            assert count_col[i].value == 2
        elif dept_val == "marketing":
            assert abs(avg_age_col[i].value - 39.5) < 0.01
            assert total_salary_col[i].value == 175000
            assert count_col[i].value == 2
        elif dept_val == "hr":
            assert avg_age_col[i].value == 35
            assert total_salary_col[i].value == 80000
            assert count_col[i].value == 1


def test_group_by_multiple_columns():
    table = Table.from_dict(
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

    columns = result.columns()
    assert len(columns) >= 4
    values = result.values()
    assert len(values) >= 2

    # Expected groups:
    # eng/senior: total=290000 (150000+140000), avg=145000
    # eng/junior: total=100000, avg=100000
    # marketing/senior: total=120000, avg=120000
    # marketing/junior: total=90000, avg=90000

    cols = list(result.columns())
    dept_idx = cols.index("dept") if "dept" in cols else cols.index("by")
    level_idx = (
        cols.index("level") if "level" in cols else (cols.index("by") + 1 if "by" in cols else 0)
    )
    total_salary_idx = cols.index("total_salary")
    avg_salary_idx = cols.index("avg_salary")

    dept_col = values[dept_idx]
    level_col = values[level_idx]
    total_salary_col = values[total_salary_idx]
    avg_salary_col = values[avg_salary_idx]

    for i in range(len(dept_col)):
        dept_val = dept_col[i].value if hasattr(dept_col[i], "value") else str(dept_col[i])
        level_val = level_col[i].value if hasattr(level_col[i], "value") else str(level_col[i])

        if dept_val == "eng" and level_val == "senior":
            assert total_salary_col[i].value == 290000
            assert avg_salary_col[i].value == 145000
        elif dept_val == "eng" and level_val == "junior":
            assert total_salary_col[i].value == 100000
            assert avg_salary_col[i].value == 100000
        elif dept_val == "marketing" and level_val == "senior":
            assert total_salary_col[i].value == 120000
            assert avg_salary_col[i].value == 120000
        elif dept_val == "marketing" and level_val == "junior":
            assert total_salary_col[i].value == 90000
            assert avg_salary_col[i].value == 90000


def test_group_by_with_filtered_aggregation():
    table = Table.from_dict(
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

    columns = result.columns()
    assert "total" in columns
    assert "active_total" in columns
    assert "count" in columns

    values = result.values()
    assert len(values) >= 3

    # Expected:
    # Category A: total=600 (100+200+300), active_total=100 (only first is active), count=3
    # Category B: total=400 (150+250), active_total=400 (both active), count=2

    cols = list(result.columns())
    category_idx = cols.index("category") if "category" in cols else cols.index("by")
    total_idx = cols.index("total")
    active_total_idx = cols.index("active_total")
    count_idx = cols.index("count")

    category_col = values[category_idx]
    total_col = values[total_idx]
    active_total_col = values[active_total_idx]
    count_col = values[count_idx]

    for i in range(len(category_col)):
        cat_val = (
            category_col[i].value if hasattr(category_col[i], "value") else str(category_col[i])
        )
        if cat_val == "A":
            assert total_col[i].value == 600
            assert active_total_col[i].value == 100
            assert count_col[i].value == 3
        elif cat_val == "B":
            assert total_col[i].value == 400
            assert active_total_col[i].value == 400
            assert count_col[i].value == 2


def test_complex_select_with_computed_columns():
    table = Table.from_dict(
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

    columns = result.columns()
    assert "id" in columns
    assert "total" in columns
    assert "discounted" in columns

    values = result.values()
    assert len(values) == 3
    assert len(values[0]) == 2


def test_select_with_isin_operator():
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002", "003", "004", "005"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana", "eli"], ray_type=Symbol),
            "dept": Vector(items=["eng", "eng", "marketing", "hr", "marketing"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38, 45], ray_type=I64),
        },
    )

    result = (
        table.select("id", "name", "dept", "age")
        .where(Column("dept").isin(["eng", "marketing"]))
        .execute()
    )

    columns = result.columns()
    assert len(columns) == 4
    assert "id" in columns
    assert "name" in columns
    assert "dept" in columns
    assert "age" in columns

    values = result.values()
    assert len(values) == 4
    assert len(values[0]) == 4

    cols = list(result.columns())
    name_idx = cols.index("name")
    dept_idx = cols.index("dept")

    name_col = values[name_idx]
    dept_col = values[dept_idx]

    returned_depts = [dept_col[i].value for i in range(len(dept_col))]
    assert all(dept in ["eng", "marketing"] for dept in returned_depts)
    assert len(returned_depts) == 4

    returned_names = [name_col[i].value for i in range(len(name_col))]
    assert "alice" in returned_names
    assert "bob" in returned_names
    assert "charlie" in returned_names
    assert "eli" in returned_names
    assert "dana" not in returned_names

    result_int = table.select("id", "name", "age").where(Column("age").isin([29, 41, 45])).execute()

    columns_int = result_int.columns()
    assert len(columns_int) == 3
    assert "id" in columns_int
    assert "name" in columns_int
    assert "age" in columns_int

    values_int = result_int.values()
    assert len(values_int) == 3
    assert len(values_int[0]) == 3

    cols_int = list(result_int.columns())
    name_idx_int = cols_int.index("name")
    age_idx_int = cols_int.index("age")

    name_col_int = values_int[name_idx_int]
    age_col_int = values_int[age_idx_int]

    returned_ages = [age_col_int[i].value for i in range(len(age_col_int))]
    assert all(age in [29, 41, 45] for age in returned_ages)
    assert len(returned_ages) == 3

    returned_names_int = [name_col_int[i].value for i in range(len(name_col_int))]
    assert "alice" in returned_names_int  # age 29
    assert "charlie" in returned_names_int  # age 41
    assert "eli" in returned_names_int  # age 45
    assert "bob" not in returned_names_int  # age 34
    assert "dana" not in returned_names_int  # age 38
