import pytest

from rayforce import F64, I64, Symbol, Table, Vector


@pytest.fixture
def sqlglot():
    try:
        import sqlglot

        return sqlglot
    except ImportError:
        pytest.skip("sqlglot is not installed")


@pytest.fixture
def sample_table():
    return Table(
        {
            "id": Vector([1, 2, 3, 4, 5], ray_type=I64),
            "name": Vector(["Alice", "Bob", "Charlie", "Diana", "Eve"], ray_type=Symbol),
            "age": Vector([25, 30, 35, 28, 32], ray_type=I64),
            "salary": Vector([50000.0, 60000.0, 70000.0, 55000.0, 65000.0], ray_type=F64),
            "dept": Vector(["eng", "sales", "eng", "sales", "eng"], ray_type=Symbol),
        }
    )


def test_select_all(sqlglot, sample_table):
    result = sample_table.sql("SELECT * FROM self")
    assert len(result.columns()) == 5


def test_select_columns(sqlglot, sample_table):
    result = sample_table.sql("SELECT name, age FROM self")
    columns = [str(c) for c in result.columns()]
    assert "name" in columns
    assert "age" in columns
    assert len(columns) == 2


def test_select_with_alias(sqlglot, sample_table):
    result = sample_table.sql("SELECT name AS employee_name, age AS years FROM self")
    columns = [str(c) for c in result.columns()]
    assert "employee_name" in columns
    assert "years" in columns


def test_where_equals(sqlglot, sample_table):
    result = sample_table.sql("SELECT * FROM self WHERE age = 30")
    assert len(result) == 1
    assert result["name"][0].value == "Bob"


def test_where_greater_than(sqlglot, sample_table):
    result = sample_table.sql("SELECT * FROM self WHERE age > 30")
    assert len(result) == 2  # Charlie (35), Eve (32)


def test_where_less_than(sqlglot, sample_table):
    result = sample_table.sql("SELECT * FROM self WHERE age < 30")
    assert len(result) == 2  # Alice (25), Diana (28)


def test_where_and(sqlglot, sample_table):
    result = sample_table.sql("SELECT * FROM self WHERE age > 25 AND age < 35")
    assert len(result) == 3  # Bob (30), Diana (28), Eve (32)


def test_where_or(sqlglot, sample_table):
    result = sample_table.sql("SELECT * FROM self WHERE age = 25 OR age = 35")
    assert len(result) == 2  # Alice (25), Charlie (35)


def test_group_by_count(sqlglot, sample_table):
    result = sample_table.sql("SELECT dept, COUNT(id) AS cnt FROM self GROUP BY dept")
    assert len(result) == 2  # eng, sales


def test_group_by_sum(sqlglot, sample_table):
    result = sample_table.sql("SELECT dept, SUM(salary) AS total FROM self GROUP BY dept")
    assert len(result) == 2


def test_group_by_avg(sqlglot, sample_table):
    result = sample_table.sql("SELECT dept, AVG(age) AS avg_age FROM self GROUP BY dept")
    assert len(result) == 2


def test_order_by_asc(sqlglot, sample_table):
    result = sample_table.sql("SELECT * FROM self ORDER BY age")
    ages = [v.value for v in result["age"]]
    assert ages == sorted(ages)


def test_order_by_desc(sqlglot, sample_table):
    result = sample_table.sql("SELECT * FROM self ORDER BY age DESC")
    ages = [v.value for v in result["age"]]
    assert ages == sorted(ages, reverse=True)


def test_where_in(sqlglot, sample_table):
    result = sample_table.sql("SELECT * FROM self WHERE age IN (25, 30, 35)")
    assert len(result) == 3


def test_arithmetic_expression(sqlglot, sample_table):
    result = sample_table.sql("SELECT salary * 1.1 AS new_salary FROM self")
    columns = [str(c) for c in result.columns()]
    assert "new_salary" in columns


def test_combined_where_and_group(sqlglot, sample_table):
    result = sample_table.sql(
        "SELECT dept, AVG(salary) AS avg_sal FROM self WHERE age > 25 GROUP BY dept"
    )
    assert len(result) == 2


def test_combined_where_group_order(sqlglot, sample_table):
    result = sample_table.sql(
        "SELECT dept, COUNT(id) AS cnt FROM self WHERE salary > 50000 GROUP BY dept ORDER BY cnt DESC"
    )
    assert len(result) == 2


def test_min_max(sqlglot, sample_table):
    result = sample_table.sql("SELECT MIN(age) AS min_age, MAX(age) AS max_age FROM self")
    assert result["min_age"][0].value == 25
    assert result["max_age"][0].value == 35


def test_parenthesized_or(sqlglot, sample_table):
    # Test (A OR B) AND C pattern
    result = sample_table.sql(
        "SELECT * FROM self WHERE (dept = 'eng' OR dept = 'sales') AND age > 28"
    )
    assert len(result) >= 1


def test_complex_aggregation(sqlglot, sample_table):
    result = sample_table.sql("""
        SELECT
            dept,
            AVG(salary) AS avg_sal,
            MAX(age) AS max_age,
            COUNT(id) AS cnt
        FROM self
        WHERE age > 25
        GROUP BY dept
        ORDER BY avg_sal DESC
    """)
    assert len(result) == 2  # eng and sales have people > 25


def test_update_single_column(sqlglot, sample_table):
    result = sample_table.sql("UPDATE self SET salary = 99999.0 WHERE id = 1")
    # Find the row with id=1 and check salary
    for i, id_val in enumerate(result["id"]):
        if id_val.value == 1:
            assert result["salary"][i].value == 99999.0
            break


def test_update_all_rows(sqlglot, sample_table):
    result = sample_table.sql("UPDATE self SET age = 100")
    for age_val in result["age"]:
        assert age_val.value == 100


def test_update_with_expression(sqlglot, sample_table):
    result = sample_table.sql("UPDATE self SET salary = salary + 1000.0 WHERE age > 30")
    # Original salaries were 50000, 60000, 70000, 55000, 65000
    # Ages > 30: Charlie (35, 70000->71000), Eve (32, 65000->66000)
    for i, age_val in enumerate(result["age"]):
        if age_val.value > 30:
            assert result["salary"][i].value > 65000  # All updated values should be > 65000


def test_update_multiple_columns(sqlglot, sample_table):
    result = sample_table.sql("UPDATE self SET age = 99, salary = 1.0 WHERE id = 2")
    for i, id_val in enumerate(result["id"]):
        if id_val.value == 2:
            assert result["age"][i].value == 99
            assert result["salary"][i].value == 1.0
            break


def test_update_with_complex_where(sqlglot, sample_table):
    result = sample_table.sql(
        "UPDATE self SET salary = 0.0 WHERE (dept = 'eng' OR dept = 'sales') AND age < 30"
    )
    # Should update Alice (eng, 25) and Diana (sales, 28)
    updated_count = sum(1 for s in result["salary"] if s.value == 0.0)
    assert updated_count == 2


def test_insert_single_row_with_columns(sqlglot):
    table = Table(
        {
            "id": Vector([1, 2], ray_type=I64),
            "name": Vector(["Alice", "Bob"], ray_type=Symbol),
        }
    )
    result = table.sql("INSERT INTO self (id, name) VALUES (3, 'Charlie')")
    assert len(result) == 3
    assert result["id"][2].value == 3
    assert result["name"][2].value == "Charlie"


def test_insert_multiple_rows_with_columns(sqlglot):
    table = Table(
        {
            "id": Vector([1], ray_type=I64),
            "name": Vector(["Alice"], ray_type=Symbol),
        }
    )
    result = table.sql("INSERT INTO self (id, name) VALUES (2, 'Bob'), (3, 'Charlie')")
    assert len(result) == 3
    ids = [v.value for v in result["id"]]
    assert ids == [1, 2, 3]


def test_insert_without_columns(sqlglot):
    table = Table(
        {
            "id": Vector([1], ray_type=I64),
            "name": Vector(["Alice"], ray_type=Symbol),
        }
    )
    result = table.sql("INSERT INTO self VALUES (2, 'Bob')")
    assert len(result) == 2
    assert result["id"][1].value == 2
    assert result["name"][1].value == "Bob"


def test_insert_multiple_rows_without_columns(sqlglot):
    table = Table(
        {
            "id": Vector([1], ray_type=I64),
            "name": Vector(["Alice"], ray_type=Symbol),
        }
    )
    result = table.sql("INSERT INTO self VALUES (2, 'Bob'), (3, 'Charlie')")
    assert len(result) == 3


def test_insert_with_float_values(sqlglot):
    table = Table(
        {
            "id": Vector([1], ray_type=I64),
            "price": Vector([10.5], ray_type=F64),
        }
    )
    result = table.sql("INSERT INTO self (id, price) VALUES (2, 20.5)")
    assert len(result) == 2
    assert result["price"][1].value == 20.5


def test_insert_with_negative_values(sqlglot):
    table = Table(
        {
            "id": Vector([1], ray_type=I64),
            "value": Vector([100], ray_type=I64),
        }
    )
    result = table.sql("INSERT INTO self (id, value) VALUES (2, -50)")
    assert len(result) == 2
    assert result["value"][1].value == -50


def test_upsert_update_existing(sqlglot):
    table = Table(
        {
            "id": Vector([1, 2], ray_type=I64),
            "name": Vector(["Alice", "Bob"], ray_type=Symbol),
        }
    )
    result = table.sql(
        "INSERT INTO self (id, name) VALUES (1, 'Alice Updated') ON CONFLICT (id) DO UPDATE"
    )
    assert len(result) == 2
    # Find row with id=1 and verify name was updated
    for i, id_val in enumerate(result["id"]):
        if id_val.value == 1:
            assert result["name"][i].value == "Alice Updated"
            break


def test_upsert_insert_new(sqlglot):
    table = Table(
        {
            "id": Vector([1, 2], ray_type=I64),
            "name": Vector(["Alice", "Bob"], ray_type=Symbol),
        }
    )
    result = table.sql(
        "INSERT INTO self (id, name) VALUES (3, 'Charlie') ON CONFLICT (id) DO UPDATE"
    )
    assert len(result) == 3
    ids = [v.value for v in result["id"]]
    assert 3 in ids


def test_upsert_multiple_rows(sqlglot):
    table = Table(
        {
            "id": Vector([1], ray_type=I64),
            "name": Vector(["Alice"], ray_type=Symbol),
        }
    )
    result = table.sql("""
        INSERT INTO self (id, name)
        VALUES (1, 'Alice Updated'), (2, 'Bob')
        ON CONFLICT (id) DO UPDATE
    """)
    assert len(result) == 2
    names = [v.value for v in result["name"]]
    assert "Alice Updated" in names
    assert "Bob" in names


def test_upsert_composite_key(sqlglot):
    table = Table(
        {
            "region": Vector(["US", "EU"], ray_type=Symbol),
            "id": Vector([1, 1], ray_type=I64),
            "value": Vector([100, 200], ray_type=I64),
        }
    )
    # Use first 2 columns as composite key
    result = table.sql("""
        INSERT INTO self (region, id, value)
        VALUES ('US', 1, 150)
        ON CONFLICT (region, id) DO UPDATE
    """)
    assert len(result) == 2
    # Find US/1 row and verify value was updated
    for i, region in enumerate(result["region"]):
        if region.value == "US" and result["id"][i].value == 1:
            assert result["value"][i].value == 150
            break


def test_upsert_do_nothing_raises(sqlglot):
    table = Table(
        {
            "id": Vector([1], ray_type=I64),
            "name": Vector(["Alice"], ray_type=Symbol),
        }
    )
    with pytest.raises(ValueError, match="DO NOTHING is not supported"):
        table.sql("INSERT INTO self (id, name) VALUES (1, 'Bob') ON CONFLICT (id) DO NOTHING")


def test_upsert_mismatched_key_raises(sqlglot):
    table = Table(
        {
            "id": Vector([1], ray_type=I64),
            "name": Vector(["Alice"], ray_type=Symbol),
        }
    )
    with pytest.raises(ValueError, match="must match the first"):
        table.sql("INSERT INTO self (id, name) VALUES (1, 'Bob') ON CONFLICT (name) DO UPDATE")


def test_invalid_sql_raises(sqlglot, sample_table):
    with pytest.raises(ValueError, match="Statement not supported"):
        sample_table.sql("DELETE FROM self WHERE id = 1")


def test_negative_number(sqlglot, sample_table):
    result = sample_table.sql("SELECT * FROM self WHERE salary > -100")
    assert len(result) == 5


def test_empty_result(sqlglot, sample_table):
    result = sample_table.sql("SELECT * FROM self WHERE salary > 999999")
    assert len(result) == 0


def test_nested_parentheses(sqlglot, sample_table):
    result = sample_table.sql(
        "SELECT * FROM self WHERE ((dept = 'eng' OR dept = 'sales') AND age > 28) OR age = 25"
    )
    assert len(result) >= 2


def test_deeply_nested_logic(sqlglot, sample_table):
    result = sample_table.sql(
        "SELECT * FROM self WHERE dept = 'eng' AND (age > 30 OR (salary > 60000 AND age >= 25))"
    )
    assert len(result) >= 1


def test_multiple_aggregations_no_group(sqlglot, sample_table):
    result = sample_table.sql(
        "SELECT COUNT(id) AS cnt, AVG(salary) AS avg_sal, MIN(age) AS min_age, MAX(age) AS max_age FROM self"
    )
    assert result["cnt"][0].value == 5


def test_range_with_and(sqlglot, sample_table):
    result = sample_table.sql("SELECT * FROM self WHERE age >= 28 AND age <= 32")
    assert len(result) >= 2


def test_float_comparison(sqlglot, sample_table):
    result = sample_table.sql("SELECT * FROM self WHERE salary > 55000.5")
    assert len(result) >= 2


def test_arithmetic_subtraction(sqlglot, sample_table):
    result = sample_table.sql("SELECT name, salary - 10000 AS adjusted FROM self")
    assert "adjusted" in [str(c) for c in result.columns()]


def test_arithmetic_division(sqlglot, sample_table):
    result = sample_table.sql("SELECT name, salary / 12 AS monthly FROM self")
    assert "monthly" in [str(c) for c in result.columns()]


def test_in_combined_with_and(sqlglot, sample_table):
    result = sample_table.sql("SELECT * FROM self WHERE dept IN ('eng', 'sales') AND age > 28")
    assert len(result) >= 1


# SQLQuery IPC tests
def test_sql_query_ipc_select(sqlglot):
    from rayforce.plugins.sql import SQLQuery

    query = SQLQuery("employees", "SELECT name, age FROM self WHERE age > 30")
    assert query.ipc is not None


def test_sql_query_ipc_update(sqlglot):
    from rayforce.plugins.sql import SQLQuery

    query = SQLQuery("employees", "UPDATE self SET salary = 100000.0 WHERE level = 'senior'")
    assert query.ipc is not None


def test_sql_query_ipc_insert(sqlglot):
    from rayforce.plugins.sql import SQLQuery

    query = SQLQuery("employees", "INSERT INTO self (id, name) VALUES (1, 'Alice')")
    assert query.ipc is not None


def test_sql_query_ipc_upsert(sqlglot):
    from rayforce.plugins.sql import SQLQuery

    query = SQLQuery(
        "employees", "INSERT INTO self (id, name) VALUES (1, 'Alice') ON CONFLICT (id) DO UPDATE"
    )
    assert query.ipc is not None


def test_sql_query_stores_parsed(sqlglot):
    from rayforce.plugins.sql import ParsedSelect, SQLQuery

    query = SQLQuery("employees", "SELECT * FROM self")
    assert isinstance(query._parsed, ParsedSelect)
    assert query.table_name == "employees"
    assert query.query_str == "SELECT * FROM self"


def test_missing_sqlglot_raises(monkeypatch):
    import importlib
    import sys

    from rayforce.plugins import sql as sql_module

    original_sqlglot = sys.modules.get("sqlglot")
    if "sqlglot" in sys.modules:
        del sys.modules["sqlglot"]

    original_import = __import__

    def mock_import(name, *args, **kwargs):
        if name == "sqlglot":
            raise ImportError("No module named 'sqlglot'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", mock_import)

    importlib.reload(sql_module)

    from rayforce.plugins.sql import _ensure_sqlglot

    with pytest.raises(ImportError, match="sqlglot is required"):
        _ensure_sqlglot()

    # Restore sqlglot and reload the module to restore proper state
    if original_sqlglot:
        sys.modules["sqlglot"] = original_sqlglot
    monkeypatch.undo()
    importlib.reload(sql_module)
