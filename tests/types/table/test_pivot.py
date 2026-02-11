from rayforce import I64, Symbol, Table, Vector
from tests.helpers.assertions import assert_contains_columns, assert_table_shape


def _get_pivot_values(result, index_col: str) -> dict:
    """Build {index_value: {col: value, ...}} dict from a pivot result."""
    index_values = [v.to_python() for v in result[index_col]]
    columns = [str(c) for c in result.columns() if str(c) != index_col]
    return {
        idx_val: {col: result[col][i].to_python() for col in columns}
        for i, idx_val in enumerate(index_values)
    }


def test_pivot_simple():
    table = Table(
        {
            "symbol": Vector(items=["AAPL", "AAPL", "GOOG", "GOOG"], ray_type=Symbol),
            "metric": Vector(items=["price", "volume", "price", "volume"], ray_type=Symbol),
            "value": Vector(items=[150, 1000, 2800, 500], ray_type=I64),
        }
    )

    result = table.pivot(index="symbol", columns="metric", values="value", aggfunc="min").execute()

    assert_contains_columns(result, ["symbol", "price", "volume"])
    assert_table_shape(result, rows=2, cols=3)

    pv = _get_pivot_values(result, "symbol")
    assert pv["AAPL"] == {"price": 150, "volume": 1000}
    assert pv["GOOG"] == {"price": 2800, "volume": 500}


def test_pivot_with_multiple_index_columns():
    table = Table(
        {
            "date": Vector(
                items=["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"], ray_type=Symbol
            ),
            "symbol": Vector(items=["AAPL", "AAPL", "AAPL", "AAPL"], ray_type=Symbol),
            "metric": Vector(items=["open", "close", "open", "close"], ray_type=Symbol),
            "value": Vector(items=[150, 152, 153, 155], ray_type=I64),
        }
    )

    result = table.pivot(
        index=["date", "symbol"], columns="metric", values="value", aggfunc="min"
    ).execute()

    assert_contains_columns(result, ["date", "symbol", "open", "close"])
    assert_table_shape(result, rows=2, cols=4)

    pv = _get_pivot_values(result, "date")
    assert pv["2024-01-01"]["open"] == 150
    assert pv["2024-01-01"]["close"] == 152
    assert pv["2024-01-02"]["open"] == 153
    assert pv["2024-01-02"]["close"] == 155


def test_pivot_with_sum_aggfunc():
    table = Table(
        {
            "category": Vector(items=["A", "A", "A", "B", "B"], ray_type=Symbol),
            "type": Vector(items=["x", "x", "y", "x", "y"], ray_type=Symbol),
            "value": Vector(items=[10, 20, 30, 40, 50], ray_type=I64),
        }
    )

    result = table.pivot(index="category", columns="type", values="value", aggfunc="sum").execute()

    assert_contains_columns(result, ["category", "x", "y"])
    assert_table_shape(result, rows=2, cols=3)

    pv = _get_pivot_values(result, "category")
    assert pv["A"] == {"x": 30, "y": 30}
    assert pv["B"] == {"x": 40, "y": 50}


def test_pivot_with_count_aggfunc():
    table = Table(
        {
            "category": Vector(items=["A", "A", "A", "B", "B"], ray_type=Symbol),
            "type": Vector(items=["x", "x", "y", "x", "y"], ray_type=Symbol),
            "value": Vector(items=[10, 20, 30, 40, 50], ray_type=I64),
        }
    )

    result = table.pivot(
        index="category", columns="type", values="value", aggfunc="count"
    ).execute()

    assert_table_shape(result, rows=2, cols=3)

    pv = _get_pivot_values(result, "category")
    assert pv["A"] == {"x": 2, "y": 1}
    assert pv["B"] == {"x": 1, "y": 1}


def test_pivot_with_avg_aggfunc():
    table = Table(
        {
            "category": Vector(items=["A", "A", "B"], ray_type=Symbol),
            "metric": Vector(items=["x", "x", "x"], ray_type=Symbol),
            "value": Vector(items=[10, 20, 30], ray_type=I64),
        }
    )

    result = table.pivot(
        index="category", columns="metric", values="value", aggfunc="avg"
    ).execute()

    assert_table_shape(result, rows=2, cols=2)

    pv = _get_pivot_values(result, "category")
    assert pv["A"]["x"] == 15
    assert pv["B"]["x"] == 30


def test_pivot_with_min_aggfunc():
    table = Table(
        {
            "category": Vector(items=["A", "A", "A", "B", "B"], ray_type=Symbol),
            "type": Vector(items=["x", "x", "y", "x", "y"], ray_type=Symbol),
            "value": Vector(items=[10, 20, 30, 40, 50], ray_type=I64),
        }
    )

    result = table.pivot(index="category", columns="type", values="value", aggfunc="min").execute()

    pv = _get_pivot_values(result, "category")
    assert pv["A"] == {"x": 10, "y": 30}
    assert pv["B"] == {"x": 40, "y": 50}


def test_pivot_with_max_aggfunc():
    table = Table(
        {
            "category": Vector(items=["A", "A", "A", "B", "B"], ray_type=Symbol),
            "type": Vector(items=["x", "x", "y", "x", "y"], ray_type=Symbol),
            "value": Vector(items=[10, 20, 30, 40, 50], ray_type=I64),
        }
    )

    result = table.pivot(index="category", columns="type", values="value", aggfunc="max").execute()

    pv = _get_pivot_values(result, "category")
    assert pv["A"] == {"x": 20, "y": 30}
    assert pv["B"] == {"x": 40, "y": 50}


def test_pivot_with_first_aggfunc():
    table = Table(
        {
            "category": Vector(items=["A", "A", "A", "B", "B"], ray_type=Symbol),
            "type": Vector(items=["x", "x", "y", "x", "y"], ray_type=Symbol),
            "value": Vector(items=[10, 20, 30, 40, 50], ray_type=I64),
        }
    )

    result = table.pivot(
        index="category", columns="type", values="value", aggfunc="first"
    ).execute()

    pv = _get_pivot_values(result, "category")
    assert pv["A"] == {"x": 10, "y": 30}
    assert pv["B"] == {"x": 40, "y": 50}


def test_pivot_with_last_aggfunc():
    table = Table(
        {
            "category": Vector(items=["A", "A", "A", "B", "B"], ray_type=Symbol),
            "type": Vector(items=["x", "x", "y", "x", "y"], ray_type=Symbol),
            "value": Vector(items=[10, 20, 30, 40, 50], ray_type=I64),
        }
    )

    result = table.pivot(index="category", columns="type", values="value", aggfunc="last").execute()

    pv = _get_pivot_values(result, "category")
    assert pv["A"] == {"x": 20, "y": 30}
    assert pv["B"] == {"x": 40, "y": 50}


def test_pivot_single_value_per_cell():
    table = Table(
        {
            "row": Vector(items=["r1", "r1", "r2", "r2"], ray_type=Symbol),
            "col": Vector(items=["c1", "c2", "c1", "c2"], ray_type=Symbol),
            "val": Vector(items=[1, 2, 3, 4], ray_type=I64),
        }
    )

    result = table.pivot(index="row", columns="col", values="val", aggfunc="min").execute()

    assert_table_shape(result, rows=2, cols=3)
    assert_contains_columns(result, ["row", "c1", "c2"])

    pv = _get_pivot_values(result, "row")
    assert pv["r1"] == {"c1": 1, "c2": 2}
    assert pv["r2"] == {"c1": 3, "c2": 4}


def test_pivot_preserves_order():
    table = Table(
        {
            "id": Vector(items=["a", "a", "a"], ray_type=Symbol),
            "key": Vector(items=["third", "first", "second"], ray_type=Symbol),
            "value": Vector(items=[3, 1, 2], ray_type=I64),
        }
    )

    result = table.pivot(index="id", columns="key", values="value", aggfunc="min").execute()

    assert_contains_columns(result, ["id", "third", "first", "second"])

    pv = _get_pivot_values(result, "id")
    assert pv["a"] == {"third": 3, "first": 1, "second": 2}


def test_pivot_with_sparse_data():
    """Pivot where some index/column combinations are missing produces NULLs."""
    table = Table(
        {
            "category": Vector(items=["A", "A", "B"], ray_type=Symbol),
            "type": Vector(items=["x", "y", "x"], ray_type=Symbol),
            "value": Vector(items=[10, 20, 30], ray_type=I64),
        }
    )

    result = table.pivot(index="category", columns="type", values="value", aggfunc="sum").execute()

    assert_contains_columns(result, ["category", "x", "y"])
    assert_table_shape(result, rows=2, cols=3)

    pv = _get_pivot_values(result, "category")
    assert pv["A"] == {"x": 10, "y": 20}
    assert pv["B"]["x"] == 30
    # B has no "y" value — the result is None
    assert pv["B"]["y"] is None
