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


def test_invalid_sql_raises(sqlglot, sample_table):
    with pytest.raises(ValueError, match="Only SELECT"):
        sample_table.sql("INSERT INTO self VALUES (1, 2, 3)")


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


def test_missing_sqlglot_raises(monkeypatch):
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

    import importlib

    importlib.reload(sql_module)

    from rayforce.plugins.sql import _ensure_sqlglot

    with pytest.raises(ImportError, match="sqlglot is required"):
        _ensure_sqlglot()

    if original_sqlglot:
        sys.modules["sqlglot"] = original_sqlglot
