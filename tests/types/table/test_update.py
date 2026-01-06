import pytest
from rayforce import Table, Vector, Symbol, I64, B8, Column


@pytest.mark.parametrize("is_inplace", [True, False])
def test_update_single_row(is_inplace):
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41], ray_type=I64),
        },
    )

    if is_inplace:
        result = table.update(age=100).where(Column("id") == "001").execute()
    else:
        table.save("test_update_single")
        result = Table("test_update_single").update(age=100).where(Column("id") == "001").execute()

    assert isinstance(result, Table)
    values = result.values()

    assert len(values) == 3

    assert values[0][0].value == "001"  # id unchanged
    assert values[1][0].value == "alice"  # name unchanged
    assert values[2][0].value == 100  # age updated

    assert values[0][1].value == "002"
    assert values[1][1].value == "bob"
    assert values[2][1].value == 34  # age unchanged

    assert values[0][2].value == "003"
    assert values[1][2].value == "charlie"
    assert values[2][2].value == 41  # age unchanged


def test_update_multiple_rows():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "dept": Vector(items=["eng", "eng", "marketing"], ray_type=Symbol),
            "salary": Vector(items=[100000, 120000, 90000], ray_type=I64),
        },
    )
    table.save("test_update_multi")

    result = (
        Table("test_update_multi").update(salary=150000).where(Column("dept") == "eng").execute()
    )

    assert isinstance(result, Table)
    values = result.values()

    assert len(values) == 3

    assert values[0][0].value == "001"  # id unchanged
    assert values[1][0].value == "eng"  # dept unchanged
    assert values[2][0].value == 150000  # salary updated

    assert values[0][1].value == "002"  # id unchanged
    assert values[1][1].value == "eng"  # dept unchanged
    assert values[2][1].value == 150000  # salary updated

    assert values[0][2].value == "003"  # id unchanged
    assert values[1][2].value == "marketing"  # dept unchanged
    assert values[2][2].value == 90000  # salary unchanged


@pytest.mark.parametrize("is_inplace", [True, False])
def test_update_all_rows(is_inplace):
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "status": Vector(items=["active", "active", "inactive"], ray_type=Symbol),
            "score": Vector(items=[10, 20, 30], ray_type=I64),
        },
    )

    if is_inplace:
        result = table.update(score=0).execute()
    else:
        table.save("test_update_all")
        result = Table("test_update_all").update(score=0).execute()

    assert isinstance(result, Table)
    values = result.values()

    assert values[2][0].value == 0  # All scores should be 0
    assert values[2][1].value == 0
    assert values[2][2].value == 0

    assert values[0][0].value == "001"
    assert values[0][1].value == "002"
    assert values[0][2].value == "003"
    assert values[1][0].value == "active"
    assert values[1][1].value == "active"
    assert values[1][2].value == "inactive"


def test_update_multiple_columns():
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
            "salary": Vector(items=[50000, 60000], ray_type=I64),
        },
    )
    table.save("test_update_multi_cols")

    result = (
        Table("test_update_multi_cols")
        .update(age=30, salary=55000)
        .where(Column("id") == "001")
        .execute()
    )

    assert isinstance(result, Table)
    values = result.values()

    assert values[0][0].value == "001"  # id unchanged
    assert values[1][0].value == "alice"  # name unchanged
    assert values[2][0].value == 30  # age updated
    assert values[3][0].value == 55000  # salary updated

    assert values[0][1].value == "002"
    assert values[1][1].value == "bob"
    assert values[2][1].value == 34  # age unchanged
    assert values[3][1].value == 60000  # salary unchanged


def test_update_with_comparison_condition():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "age": Vector(items=[25, 30, 35], ray_type=I64),
            "active": Vector(items=[True, False, True], ray_type=B8),
        },
    )
    table.save("test_update_comparison")

    result = Table("test_update_comparison").update(age=99).where(Column("age") > 30).execute()

    assert isinstance(result, Table)
    values = result.values()

    assert values[1][2].value == 99

    assert values[1][0].value == 25  # age=25, not updated
    assert values[1][1].value == 30  # age=30, not updated


def test_update_with_complex_condition():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "dept": Vector(items=["eng", "eng", "marketing", "eng"], ray_type=Symbol),
            "salary": Vector(items=[100000, 120000, 90000, 110000], ray_type=I64),
        },
    )
    table.save("test_update_complex")

    result = (
        Table("test_update_complex")
        .update(salary=150000)
        .where((Column("dept") == "eng") & (Column("salary") < 115000))
        .execute()
    )

    assert isinstance(result, Table)
    values = result.values()

    assert values[2][0].value == 150000
    assert values[2][1].value == 120000
    assert values[2][2].value == 90000
    assert values[2][3].value == 150000


def test_update_no_matching_rows():
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "status": Vector(items=["active", "active"], ray_type=Symbol),
        },
    )
    table.save("test_update_no_match")

    result = (
        Table("test_update_no_match")
        .update(status="inactive")
        .where(Column("id") == "999")  # No matching row
        .execute()
    )

    assert isinstance(result, Table)
    values = result.values()

    assert values[1][0].value == "active"
    assert values[1][1].value == "active"
