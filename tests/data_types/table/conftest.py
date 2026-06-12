"""Table-specific test fixtures.

Provides ready-made Table instances and common data patterns
used across insert/select/update/upsert/join/order_by tests.
"""

from __future__ import annotations

import pytest

from rayforce import F64, I64, Symbol, Vector
from rayforce.types.scalars import Time


@pytest.fixture
def employees_table(make_table):
    """A saved 4-row employee table (id, name, dept, age, salary).

    Returns (table_name, table_reference).
    """
    return make_table(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "dept": Vector(items=["eng", "eng", "marketing", "eng"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
            "salary": Vector(items=[100000, 120000, 90000, 85000], ray_type=I64),
        },
    )


@pytest.fixture
def trades_table(make_table):
    """A saved 4-row trades table (Sym, Ts, Price).

    Returns (table_name, table_reference).
    """
    return make_table(
        {
            "Sym": Vector(items=["AAPL", "AAPL", "GOOGL", "GOOGL"], ray_type=Symbol),
            "Ts": Vector(
                items=[
                    Time("09:00:29.998"),
                    Time("09:00:20.998"),
                    Time("09:00:21.998"),
                    Time("09:00:22.998"),
                ],
                ray_type=Time,
            ),
            "Price": Vector(items=[100, 200, 300, 400], ray_type=I64),
        },
    )


@pytest.fixture
def quotes_table(make_table):
    """A saved 6-row quotes table (Sym, Ts, Bid, Ask).

    Returns (table_name, table_reference).
    """
    return make_table(
        {
            "Sym": Vector(
                items=["AAPL", "AAPL", "AAPL", "GOOGL", "GOOGL", "GOOGL"], ray_type=Symbol
            ),
            "Ts": Vector(
                items=[
                    Time("09:00:20.998"),
                    Time("09:00:21.998"),
                    Time("09:00:22.998"),
                    Time("09:00:19.998"),
                    Time("09:00:20.998"),
                    Time("09:00:21.998"),
                ],
                ray_type=Time,
            ),
            "Bid": Vector(items=[10.0, 20.0, 30.0, 40.0, 50.0, 60.0], ray_type=F64),
            "Ask": Vector(items=[11.0, 21.0, 31.0, 41.0, 51.0, 61.0], ray_type=F64),
        },
    )
