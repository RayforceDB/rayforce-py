"""
Tests for the new Pythonic/fluent syntax.

This file demonstrates the new syntax side-by-side with the old syntax,
showing how much simpler and more readable the code becomes.
"""

from raypy import Table


def test_basic_column_access():
    """Test that column access via attributes works"""
    table = Table(
        columns=["id", "name", "age"],
        values=[["001", "002"], ["alice", "bob"], [29, 34]],
    )

    # Access column
    col = table.age
    assert col.name == "age"

    # Create expression
    expr = table.age >= 30
    assert expr is not None


def test_simple_select_with_filter():
    """Test basic select with where clause"""
    table = Table(
        columns=["id", "name", "age"],
        values=[["001", "002", "003"], ["alice", "bob", "charlie"], [29, 34, 41]],
    )

    # New fluent syntax
    result = table.select("id", "name", "age").where(table.age >= 30).execute()

    # Should have 2 rows (bob and charlie)
    assert len(result.values()[0]) == 2


def test_computed_columns():
    """Test select with computed columns"""
    table = Table(
        columns=["id", "name", "age"],
        values=[["001", "002", "003"], ["alice", "bob", "charlie"], [29, 34, 41]],
    )

    # New syntax with computed column
    result = (
        table.select("id", "name", age_doubled=table.age * 2)
        .where(table.age >= 30)
        .execute()
    )

    # Check that we have the columns
    columns = result.columns  # Use property, not method
    assert "age_doubled" in columns


def test_complex_filter_conditions():
    """Test complex AND/OR conditions"""
    table = Table(
        columns=["id", "name", "age", "dept"],
        values=[
            ["001", "002", "003"],
            ["alice", "bob", "charlie"],
            [29, 34, 41],
            ["eng", "marketing", "eng"],
        ],
    )

    # AND condition
    result = (
        table.select("id", "name")
        .where((table.age >= 30) & (table.dept == "eng"))
        .execute()
    )

    # Should have 1 row (charlie)
    assert len(result.values()[0]) == 1


def test_group_by_with_aggregations():
    """Test GROUP BY with aggregations"""
    table = Table(
        columns=["dept", "age", "salary"],
        values=[
            ["eng", "eng", "marketing", "marketing"],
            [29, 34, 41, 38],
            [100000, 120000, 90000, 85000],
        ],
    )

    # Group by with aggregations
    result = table.group_by("dept").agg(
        total_salary=table.salary.sum(), avg_age=table.age.mean()
    )

    # Should have 2 groups (eng and marketing)
    columns = result.columns  # Use property, not method
    assert "total_salary" in columns
    assert "avg_age" in columns


def test_filtered_aggregation():
    """Test conditional aggregation like: column.where(condition).sum()"""
    table = Table(
        columns=["category", "amount", "status"],
        values=[
            ["A", "A", "B", "B"],
            [100, 200, 150, 250],
            ["active", "inactive", "active", "active"],
        ],
    )

    # Conditional aggregation
    result = table.group_by("category").agg(
        total_all=table.amount.sum(),
        total_active=table.amount.where(table.status == "active").sum(),
    )

    columns = result.columns  # Use property, not method
    assert "total_all" in columns
    assert "total_active" in columns


def test_isin_filter():
    """Test the .isin() method for membership checking"""
    table = Table(
        columns=["id", "dept", "age"],
        values=[
            ["001", "002", "003", "004"],
            ["eng", "marketing", "hr", "eng"],
            [29, 34, 41, 38],
        ],
    )

    # Filter using isin
    result = (
        table.select("id", "dept", "age")
        .where(table.dept.isin(["eng", "hr"]))
        .execute()
    )

    # Should have 3 rows (eng, hr, eng)
    assert len(result.values()[0]) == 3


def test_complex_query_like_user_example():
    """
    Test a complex query similar to the user's exec_costs example.

    This demonstrates the most advanced features:
    - GROUP BY multiple columns
    - Multiple aggregations
    - Conditional aggregation with .where()
    - .isin() for membership testing
    """
    # Create mock executed_orders table
    executed_orders = Table(
        columns=["Entity", "Broker", "Client", "ExecQty", "ExecCapacity", "ClientComm"],
        values=[
            ["A", "A", "B", "B"],
            ["B1", "B1", "B2", "B2"],
            ["C1", "C2", "C1", "C2"],
            [100, 200, 150, 250],
            ["Principal", "Agent", "CrossAsPrincipal", "Principal"],
            [10, 20, 15, 25],
        ],
    )

    # The new Pythonic syntax!
    exec_costs = executed_orders.group_by("Entity", "Broker", "Client").agg(
        ExecQty=executed_orders.ExecQty.sum(),
        ExecQtyP=executed_orders.ExecQty.where(
            executed_orders.ExecCapacity.isin(["CrossAsPrincipal", "Principal"])
        ).sum(),
        ClientComm=executed_orders.ClientComm.sum(),
    )

    # Verify the result has the expected columns
    columns = exec_costs.columns  # Use property, not method
    assert "ExecQty" in columns
    assert "ExecQtyP" in columns
    assert "ClientComm" in columns


def test_table_from_dict():
    """Test creating table from dict"""
    table = Table.from_dict(
        {"id": ["001", "002"], "name": ["alice", "bob"], "age": [29, 34]}
    )

    assert table.columns == ["id", "name", "age"]


def test_table_from_records():
    """Test creating table from list of records"""
    table = Table.from_records(
        [
            {"id": "001", "name": "alice", "age": 29},
            {"id": "002", "name": "bob", "age": 34},
        ]
    )

    assert table.columns == ["id", "name", "age"]


def test_update_query():
    """Test UPDATE syntax"""
    table = Table(columns=["id", "age"], values=[["001", "002"], [29, 34]])
    table.save("test_table")

    # Update with filter
    table_1 = Table.get("test_table")
    result = table_1.update(age=100).where(table_1.age == 34).execute()

    # Check result
    assert result is not None
