import pytest

from rayforce import I64, Column, Symbol, Table, Vector


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_desc(is_inplace):
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
        },
    )

    if is_inplace:
        result = table.sort_desc(Column("age"))
    else:
        table.save("test_order_desc")
        result = Table("test_order_desc").sort_desc(Column("age"))

    assert isinstance(result, Table)
    values = result.values()

    # Verify descending order: 41 > 38 > 34 > 29
    assert values[2][0].value == 41
    assert values[2][1].value == 38
    assert values[2][2].value == 34
    assert values[2][3].value == 29

    # Verify all ages are present (no data loss)
    ages = [values[2][i].value for i in range(4)]
    assert set(ages) == {29, 34, 38, 41}

    # Verify other columns are reordered correctly with age
    # Row with age=41 should have id="003", name="charlie"
    age_41_idx = ages.index(41)
    assert values[0][age_41_idx].value == "003"
    assert values[1][age_41_idx].value == "charlie"


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_asc(is_inplace):
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
        },
    )

    if is_inplace:
        result = table.sort_asc(Column("age"))
    else:
        table.save("test_order_asc")
        result = Table("test_order_asc").sort_asc(Column("age"))

    assert isinstance(result, Table)
    values = result.values()

    # Verify ascending order: 29 < 34 < 38 < 41
    assert values[2][0].value == 29  # First row should be lowest age
    assert values[2][1].value == 34
    assert values[2][2].value == 38
    assert values[2][3].value == 41  # Last row should be highest age

    # Verify all ages are present (no data loss)
    ages = [values[2][i].value for i in range(4)]
    assert set(ages) == {29, 34, 38, 41}

    # Verify other columns are reordered correctly with age
    # Row with age=29 should have id="001", name="alice"
    age_29_idx = ages.index(29)
    assert values[0][age_29_idx].value == "001"
    assert values[1][age_29_idx].value == "alice"


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_multiple_columns(is_inplace):
    """Test ordering by multiple columns."""
    table = Table(
        {
            "dept": Vector(items=["eng", "eng", "marketing", "marketing"], ray_type=Symbol),
            "salary": Vector(items=[100000, 120000, 90000, 110000], ray_type=I64),
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
        },
    )

    if is_inplace:
        result = table.sort_asc(Column("dept"), Column("salary"))
    else:
        table.save("test_order_multi")
        result = Table("test_order_multi").sort_asc(Column("dept"), Column("salary"))

    assert isinstance(result, Table)
    values = result.values()

    # Verify ordering: first by dept (asc), then by salary (asc)
    # Expected order:
    # 1. eng, 100000 (alice)
    # 2. eng, 120000 (bob)
    # 3. marketing, 90000 (charlie)
    # 4. marketing, 110000 (dana)

    assert values[0][0].value == "eng"
    assert values[1][0].value == 100000
    assert values[2][0].value == "alice"

    assert values[0][1].value == "eng"
    assert values[1][1].value == 120000
    assert values[2][1].value == "bob"

    assert values[0][2].value == "marketing"
    assert values[1][2].value == 90000
    assert values[2][2].value == "charlie"

    assert values[0][3].value == "marketing"
    assert values[1][3].value == 110000
    assert values[2][3].value == "dana"


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_string_column(is_inplace):
    """Test ordering by string column."""
    table = Table(
        {
            "id": Vector(items=["003", "001", "004", "002"], ray_type=Symbol),
            "name": Vector(items=["charlie", "alice", "dana", "bob"], ray_type=Symbol),
        },
    )

    if is_inplace:
        result = table.sort_asc(Column("name"))
    else:
        table.save("test_order_string")
        result = Table("test_order_string").sort_asc(Column("name"))

    assert isinstance(result, Table)
    values = result.values()

    # Verify alphabetical order: alice < bob < charlie < dana
    assert values[1][0].value == "alice"
    assert values[1][1].value == "bob"
    assert values[1][2].value == "charlie"
    assert values[1][3].value == "dana"

    # Verify ids are reordered correctly with names
    assert values[0][0].value == "001"  # alice's id
    assert values[0][1].value == "002"  # bob's id
    assert values[0][2].value == "003"  # charlie's id
    assert values[0][3].value == "004"  # dana's id


@pytest.mark.parametrize("is_inplace", [True, False])
def test_order_by_preserves_all_rows(is_inplace):
    """Test that ordering preserves all rows and columns."""
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "value": Vector(items=[3, 1, 2], ray_type=I64),
        },
    )

    if is_inplace:
        result = table.sort_asc(Column("value"))
    else:
        table.save("test_order_preserve")
        result = Table("test_order_preserve").sort_asc(Column("value"))

    assert isinstance(result, Table)

    # Verify table structure preserved
    columns = result.columns()
    assert len(columns) == 2
    assert "id" in columns
    assert "value" in columns

    # Verify all rows present
    values = result.values()
    assert len(values[0]) == 3  # Still 3 rows

    # Verify all values present (just reordered)
    all_values = [values[1][i].value for i in range(3)]
    assert set(all_values) == {1, 2, 3}
