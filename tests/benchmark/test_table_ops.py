"""Table operation benchmarks.

Run with: pytest tests/benchmark/ -m benchmark -v
"""

import pytest

from rayforce import F64, I64, Symbol, Table, Vector

pytestmark = pytest.mark.benchmark


@pytest.fixture()
def large_table():
    """Create a table with 10,000 rows for benchmarking."""
    num_rows = 10_000
    return Table(
        {
            "id": Vector(items=[f"id_{i:05d}" for i in range(num_rows)], ray_type=Symbol),
            "value": Vector(items=list(range(num_rows)), ray_type=I64),
            "price": Vector(items=[float(i) * 1.5 for i in range(num_rows)], ray_type=F64),
            "category": Vector(items=[f"cat_{i % 10}" for i in range(num_rows)], ray_type=Symbol),
        },
    )


def test_select_all(large_table):
    result = large_table.select("*").execute()
    assert len(result) == 10_000


def test_select_with_where(large_table):
    from rayforce import Column

    result = large_table.select("id", "value").where(Column("value") > 5000).execute()
    assert len(result) > 0


def test_shape(large_table):
    result = large_table.shape()
    assert result == (10_000, 4)
