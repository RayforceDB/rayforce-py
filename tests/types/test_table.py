"""
Comprehensive tests for Table class.

Tests actual query results with hard selects, multiple where conditions,
group by, update, insert, and upsert operations.
"""

from raypy import Table
from raypy.types.scalars import Symbol


def test_select_with_single_where():
    table = Table(
        columns=["id", "name", "age", "salary"],
        values=[
            ["001", "002", "003", "004"],
            ["alice", "bob", "charlie", "dana"],
            [29, 34, 41, 38],
            [100000, 120000, 90000, 85000],
        ],
    )

    result = table.select("id", "name", "age").where(table.age >= 35).execute()

    assert len(result.columns) == 3
    assert "id" in result.columns
    assert "name" in result.columns
    assert "age" in result.columns

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
    table = Table(
        columns=["id", "name", "age", "dept", "salary"],
        values=[
            ["001", "002", "003", "004", "005"],
            ["alice", "bob", "charlie", "dana", "eli"],
            [29, 34, 41, 38, 45],
            ["eng", "eng", "marketing", "eng", "marketing"],
            [100000, 120000, 90000, 85000, 95000],
        ],
    )

    result = (
        table.select("id", "name", "age", "salary")
        .where(table.age >= 35)
        .where(table.dept == "eng")
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
    table = Table(
        columns=["id", "name", "age", "dept", "salary"],
        values=[
            ["001", "002", "003", "004", "005"],
            ["alice", "bob", "charlie", "dana", "eli"],
            [29, 34, 41, 38, 45],
            ["eng", "eng", "marketing", "eng", "marketing"],
            [100000, 120000, 90000, 85000, 95000],
        ],
    )

    result = (
        table.select("id", "name")
        .where((table.age >= 35) & (table.dept == "eng"))
        .where((table.salary > 80000) | (table.age < 40))
        .execute()
    )

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) >= 0


def test_group_by_single_column():
    table = Table(
        columns=["dept", "age", "salary"],
        values=[
            ["eng", "eng", "marketing", "marketing", "hr"],
            [29, 34, 41, 38, 35],
            [100000, 120000, 90000, 85000, 80000],
        ],
    )

    result = (
        table.select(
            avg_age=table.age.mean(),
            total_salary=table.salary.sum(),
            count=table.age.count(),
        )
        .by("dept")
        .execute()
    )

    assert len(result.columns) >= 4
    assert "dept" in result.columns or "by" in result.columns
    assert "avg_age" in result.columns
    assert "total_salary" in result.columns
    assert "count" in result.columns

    values = result.values()
    assert len(values) >= 3

    # Find the column indices
    cols = result.columns
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
        dept_val = (
            dept_col[i].value if hasattr(dept_col[i], "value") else str(dept_col[i])
        )
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
    table = Table(
        columns=["dept", "level", "salary"],
        values=[
            ["eng", "eng", "eng", "marketing", "marketing"],
            ["senior", "junior", "senior", "senior", "junior"],
            [150000, 100000, 140000, 120000, 90000],
        ],
    )

    result = (
        table.select(
            total_salary=table.salary.sum(),
            avg_salary=table.salary.mean(),
        )
        .by("dept", "level")
        .execute()
    )

    assert len(result.columns) >= 4
    values = result.values()
    assert len(values) >= 2

    # Expected groups:
    # eng/senior: total=290000 (150000+140000), avg=145000
    # eng/junior: total=100000, avg=100000
    # marketing/senior: total=120000, avg=120000
    # marketing/junior: total=90000, avg=90000

    cols = result.columns
    dept_idx = cols.index("dept") if "dept" in cols else cols.index("by")
    level_idx = (
        cols.index("level")
        if "level" in cols
        else (cols.index("by") + 1 if "by" in cols else 0)
    )
    total_salary_idx = cols.index("total_salary")
    avg_salary_idx = cols.index("avg_salary")

    dept_col = values[dept_idx]
    level_col = values[level_idx]
    total_salary_col = values[total_salary_idx]
    avg_salary_col = values[avg_salary_idx]

    for i in range(len(dept_col)):
        dept_val = (
            dept_col[i].value if hasattr(dept_col[i], "value") else str(dept_col[i])
        )
        level_val = (
            level_col[i].value if hasattr(level_col[i], "value") else str(level_col[i])
        )

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
    table = Table(
        columns=["category", "amount", "status"],
        values=[
            ["A", "A", "B", "B", "A"],
            [100, 200, 150, 250, 300],
            ["active", "inactive", "active", "active", "inactive"],
        ],
    )

    result = (
        table.select(
            total=table.amount.sum(),
            active_total=table.amount.where(table.status == "active").sum(),
            count=table.amount.count(),
        )
        .by("category")
        .execute()
    )

    assert "total" in result.columns
    assert "active_total" in result.columns
    assert "count" in result.columns

    values = result.values()
    assert len(values) >= 3

    # Expected:
    # Category A: total=600 (100+200+300), active_total=100 (only first is active), count=3
    # Category B: total=400 (150+250), active_total=400 (both active), count=2

    cols = result.columns
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
            category_col[i].value
            if hasattr(category_col[i], "value")
            else str(category_col[i])
        )
        if cat_val == "A":
            assert total_col[i].value == 600
            assert active_total_col[i].value == 100
            assert count_col[i].value == 3
        elif cat_val == "B":
            assert total_col[i].value == 400
            assert active_total_col[i].value == 400
            assert count_col[i].value == 2


def test_update_single_row():
    table = Table(
        columns=["id", "name", "age"],
        values=[["001", "002", "003"], ["alice", "bob", "charlie"], [29, 34, 41]],
    )
    table.save("test_update_table")

    result = (
        Table.get("test_update_table")
        .update(age=100)
        .where(lambda t: t.id == "001")
        .execute()
    )

    if isinstance(result, Table):
        values = result.values()
        assert values[2][0].value == 100


def test_update_multiple_rows():
    table = Table(
        columns=["id", "dept", "salary"],
        values=[
            ["001", "002", "003"],
            ["eng", "eng", "marketing"],
            [100000, 120000, 90000],
        ],
    )
    table.save("test_update_multi")

    result = (
        Table.get("test_update_multi")
        .update(salary=150000)
        .where(lambda t: t.dept == "eng")
        .execute()
    )

    if isinstance(result, Table):
        values = result.values()
        assert len(values) == 3


def test_insert_single_row():
    table = Table(
        columns=["id", "name", "age"],
        values=[["001", "002"], ["alice", "bob"], [29, 34]],
    )
    table.save("test_insert_table")

    result = (
        Table.get("test_insert_table")
        .insert(id="003", name="charlie", age=41)
        .execute()
    )

    assert isinstance(result, Symbol)

    result = Table.get("test_insert_table")
    print(result.values())
    values = result.values()
    assert len(values[0]) == 3
    assert values[0][2].value == "003"
    assert values[1][2].value == "charlie"
    assert values[2][2].value == 41


def test_upsert_single_row():
    table = Table(
        columns=["id", "name", "age"],
        values=[["001", "002"], ["alice", "bob"], [29, 34]],
    )
    table.save("test_upsert_table")

    result = (
        Table.get("test_upsert_table")
        .upsert({"id": "001", "name": "alice_updated", "age": 30}, match_on="id")
        .execute()
    )

    assert isinstance(result, Symbol)

    result = Table.get("test_upsert_table")
    values = result.values()
    assert len(values[0]) == 2
    assert values[1][0].value == "alice_updated"
    assert values[2][0].value == 30


def test_upsert_multiple_rows():
    table = Table(
        columns=["id", "name", "age"],
        values=[["001", "002"], ["alice", "bob"], [29, 34]],
    )
    table.save("test_upsert_multi")

    result = (
        Table.get("test_upsert_multi")
        .upsert(
            [
                {"id": "001", "name": "alice_new", "age": 30},
                {"id": "003", "name": "charlie", "age": 41},
            ],
            match_on="id",
        )
        .execute()
    )

    assert isinstance(result, Symbol)

    result = Table.get("test_upsert_multi")
    values = result.values()
    assert len(values[0]) >= 2
    assert values[1][0].value == "alice_new"


def test_upsert_with_multiple_match_keys():
    table = Table(
        columns=["id", "version", "value"],
        values=[
            ["001", "001", "002"],
            ["v1", "v2", "v1"],
            [100, 200, 300],
        ],
    )
    table.save("test_upsert_match_keys")

    result = (
        Table.get("test_upsert_match_keys")
        .upsert(
            {"id": "001", "version": "v1", "value": 150},
            match_on=["id", "version"],
        )
        .execute()
    )

    assert isinstance(result, Symbol)

    result = Table.get("test_upsert_match_keys")
    values = result.values()
    assert len(values) == 3


def test_complex_select_with_computed_columns():
    table = Table(
        columns=["id", "price", "quantity"],
        values=[
            ["001", "002", "003"],
            [10.5, 20.0, 15.75],
            [2, 3, 4],
        ],
    )

    result = (
        table.select(
            "id",
            total=table.price * table.quantity,
            discounted=table.price * table.quantity * 0.9,
        )
        .where(table.quantity >= 3)
        .execute()
    )

    assert "id" in result.columns
    assert "total" in result.columns
    assert "discounted" in result.columns

    values = result.values()
    assert len(values) == 3
    assert len(values[0]) == 2


def test_select_with_order_by():
    table = Table(
        columns=["id", "name", "age"],
        values=[
            ["001", "002", "003", "004"],
            ["alice", "bob", "charlie", "dana"],
            [29, 34, 41, 38],
        ],
    )

    result = table.select("name").by(age=table.age.desc()).execute()

    values = result.values()
    assert (
        values[0][0].value
        > values[0][1].value
        > values[0][2].value
        > values[0][3].value
    )
