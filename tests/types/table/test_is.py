from rayforce import B8, I64, Column, List, Symbol, Table, Vector


def test_is_true_filters_true_rows():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "active": Vector(items=[True, False, True], ray_type=B8),
        },
    )

    result = table.select("name").where(Column("active").is_(True)).execute()

    values = result.values()
    cols = list(result.columns())
    name_idx = cols.index("name")
    names = [values[name_idx][i].value for i in range(len(values[name_idx]))]

    assert len(names) == 2
    assert "alice" in names
    assert "charlie" in names
    assert "bob" not in names


def test_is_true_filters_true_rows_list():
    table = Table(
        {
            "name": List(["alice", "bob", "charlie"]),
            "active": List([True, False, True]),
        },
    )

    result = table.select("name").where(Column("active").is_(True)).execute()

    values = result.values()
    cols = list(result.columns())
    name_idx = cols.index("name")
    names = [values[name_idx][i].value for i in range(len(values[name_idx]))]

    assert len(names) == 2
    assert "alice" in names
    assert "charlie" in names
    assert "bob" not in names


def test_is_false_filters_false_rows_list():
    table = Table(
        {
            "name": List(["alice", "bob", "charlie"]),
            "active": List([True, False, True]),
        },
    )

    result = table.select("name").where(Column("active").is_(False)).execute()

    values = result.values()
    cols = list(result.columns())
    name_idx = cols.index("name")
    names = [values[name_idx][i].value for i in range(len(values[name_idx]))]

    assert len(names) == 1
    assert "bob" in names


def test_is_false_filters_false_rows():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "active": Vector(items=[True, False, True], ray_type=B8),
        },
    )

    result = table.select("name").where(Column("active").is_(False)).execute()

    values = result.values()
    cols = list(result.columns())
    name_idx = cols.index("name")
    names = [values[name_idx][i].value for i in range(len(values[name_idx]))]

    assert len(names) == 1
    assert "bob" in names


def test_is_true_with_all_true():
    table = Table(
        {
            "id": Vector(items=[1, 2, 3], ray_type=I64),
            "flag": Vector(items=[True, True, True], ray_type=B8),
        },
    )

    result = table.select("id").where(Column("flag").is_(True)).execute()

    values = result.values()
    assert len(values[0]) == 3


def test_is_false_with_all_false():
    table = Table(
        {
            "id": Vector(items=[1, 2, 3], ray_type=I64),
            "flag": Vector(items=[False, False, False], ray_type=B8),
        },
    )

    result = table.select("id").where(Column("flag").is_(False)).execute()

    values = result.values()
    assert len(values[0]) == 3


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

    values = result.values()
    cols = list(result.columns())
    name_idx = cols.index("name")
    names = [values[name_idx][i].value for i in range(len(values[name_idx]))]

    assert len(names) == 2
    assert "charlie" in names
    assert "dana" in names


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

    values = result.values()
    cols = list(result.columns())
    dept_idx = cols.index("dept") if "dept" in cols else cols.index("by")
    total_idx = cols.index("active_total")

    for i in range(len(values[dept_idx])):
        dept = values[dept_idx][i].value
        total = values[total_idx][i].value
        if dept == "eng":
            assert total == 100
        elif dept == "hr":
            assert total == 400


def test_is_on_expression():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "score": Vector(items=[80, 50, 90], ray_type=I64),
        },
    )

    result = table.select("name").where((Column("score") > 60).is_(True)).execute()

    values = result.values()
    cols = list(result.columns())
    name_idx = cols.index("name")
    names = [values[name_idx][i].value for i in range(len(values[name_idx]))]

    assert len(names) == 2
    assert "alice" in names
    assert "charlie" in names
