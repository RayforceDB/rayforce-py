"""Root conftest.py — shared fixtures for all rayforce-py tests.

Provides:
- Unique table name generation (prevents shared-state flakiness)
- Table factory with automatic cleanup
- Standard sample data fixtures
"""

from __future__ import annotations

import uuid

import pytest

from rayforce import I64, Symbol, Table, Vector
from rayforce.utils.evaluation import eval_str

# ---------------------------------------------------------------------------
# Table cleanup helpers
# ---------------------------------------------------------------------------


def _delete_saved_table(name: str) -> None:
    """Best-effort deletion of a saved table from the RayforceDB environment."""
    try:
        eval_str(f"![`.;enlist `{name}]")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Core fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def table_name(request):
    """Generate a unique table name for the current test, cleaned up after use.

    Usage::

        def test_something(table_name):
            table = Table({...})
            table.save(table_name)
            result = Table(table_name).select(...)
    """
    short_id = uuid.uuid4().hex[:8]
    # Sanitise the node name: keep only alphanumerics and underscores
    node = "".join(c if c.isalnum() else "_" for c in request.node.name)[:40]
    name = f"_t_{node}_{short_id}"
    yield name
    _delete_saved_table(name)


@pytest.fixture
def make_table():
    """Factory fixture — create named tables that are automatically cleaned up.

    Usage::

        def test_something(make_table):
            t = make_table({"col": Vector(items=[1, 2], ray_type=I64)}, name="my_tbl")
            result = Table("my_tbl").select(...)

        # Or let the fixture generate a unique name:
        def test_other(make_table):
            name, tbl = make_table({"col": Vector(items=[1, 2], ray_type=I64)})
    """
    created: list[str] = []

    def _factory(data: dict, *, name: str | None = None) -> tuple[str, Table]:
        n = name or f"_t_{uuid.uuid4().hex[:12]}"
        t = Table(data)
        t.save(n)
        created.append(n)
        return n, t

    yield _factory

    for n in created:
        _delete_saved_table(n)


# ---------------------------------------------------------------------------
# Standard sample data fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def employees_data():
    """Canonical employee dataset used across table operation tests.

    Columns: id (Symbol), name (Symbol), dept (Symbol), age (I64), salary (I64)
    Rows: 4
    """
    return {
        "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
        "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
        "dept": Vector(items=["eng", "eng", "marketing", "eng"], ray_type=Symbol),
        "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
        "salary": Vector(items=[100000, 120000, 90000, 85000], ray_type=I64),
    }


@pytest.fixture
def small_table_data():
    """Minimal 2-row, 3-column dataset for simple operation tests.

    Columns: id (Symbol), name (Symbol), age (I64)
    Rows: 2
    """
    return {
        "id": Vector(items=["001", "002"], ray_type=Symbol),
        "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        "age": Vector(items=[29, 34], ray_type=I64),
    }
