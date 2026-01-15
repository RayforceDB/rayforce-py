from rayforce import I64, Symbol, Table, Vector


def _get_pivot_values(result, index_col: str) -> dict:
    index_values = [v.to_python() for v in result[index_col]]
    columns = [str(c) for c in result.columns() if str(c) != index_col]
    result_dict = {}
    for i, idx_val in enumerate(index_values):
        result_dict[idx_val] = {col: result[col][i].to_python() for col in columns}
    return result_dict


def test_pivot_simple():
    table = Table(
        {
            "symbol": Vector(items=["AAPL", "AAPL", "GOOG", "GOOG"], ray_type=Symbol),
            "metric": Vector(items=["price", "volume", "price", "volume"], ray_type=Symbol),
            "value": Vector(items=[150, 1000, 2800, 500], ray_type=I64),
        }
    )

    result = table.pivot(index="symbol", columns="metric", values="value", aggfunc="min").execute()

    columns = [str(c) for c in result.columns()]
    assert "symbol" in columns
    assert "price" in columns
    assert "volume" in columns
    assert len(result) == 2

    result_dict = _get_pivot_values(result, "symbol")
    assert result_dict["AAPL"]["price"] == 150
    assert result_dict["AAPL"]["volume"] == 1000
    assert result_dict["GOOG"]["price"] == 2800
    assert result_dict["GOOG"]["volume"] == 500


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

    columns = [str(c) for c in result.columns()]
    assert "date" in columns
    assert "symbol" in columns
    assert "open" in columns
    assert "close" in columns
    assert len(result) == 2

    result_dict = _get_pivot_values(result, "date")
    assert result_dict["2024-01-01"]["open"] == 150
    assert result_dict["2024-01-01"]["close"] == 152
    assert result_dict["2024-01-02"]["open"] == 153
    assert result_dict["2024-01-02"]["close"] == 155


def test_pivot_with_sum_aggfunc():
    table = Table(
        {
            "category": Vector(items=["A", "A", "A", "B", "B"], ray_type=Symbol),
            "type": Vector(items=["x", "x", "y", "x", "y"], ray_type=Symbol),
            "value": Vector(items=[10, 20, 30, 40, 50], ray_type=I64),
        }
    )

    result = table.pivot(index="category", columns="type", values="value", aggfunc="sum").execute()

    columns = [str(c) for c in result.columns()]
    assert "x" in columns
    assert "y" in columns
    assert len(result) == 2

    # A has x: 10+20=30, y: 30; B has x: 40, y: 50
    result_dict = _get_pivot_values(result, "category")
    assert result_dict["A"]["x"] == 30
    assert result_dict["A"]["y"] == 30
    assert result_dict["B"]["x"] == 40
    assert result_dict["B"]["y"] == 50


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

    assert len(result) == 2

    # A has x: 2, y: 1; B has x: 1, y: 1
    result_dict = _get_pivot_values(result, "category")
    assert result_dict["A"]["x"] == 2
    assert result_dict["A"]["y"] == 1
    assert result_dict["B"]["x"] == 1
    assert result_dict["B"]["y"] == 1


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

    assert len(result) == 2

    # A has x: (10+20)/2=15, B has x: 30
    result_dict = _get_pivot_values(result, "category")
    assert result_dict["A"]["x"] == 15
    assert result_dict["B"]["x"] == 30


def test_pivot_with_min_aggfunc():
    table = Table(
        {
            "category": Vector(items=["A", "A", "A", "B", "B"], ray_type=Symbol),
            "type": Vector(items=["x", "x", "y", "x", "y"], ray_type=Symbol),
            "value": Vector(items=[10, 20, 30, 40, 50], ray_type=I64),
        }
    )

    result = table.pivot(index="category", columns="type", values="value", aggfunc="min").execute()

    # A has x: min(10,20)=10, y: 30; B has x: 40, y: 50
    result_dict = _get_pivot_values(result, "category")
    assert result_dict["A"]["x"] == 10
    assert result_dict["A"]["y"] == 30
    assert result_dict["B"]["x"] == 40
    assert result_dict["B"]["y"] == 50


def test_pivot_with_max_aggfunc():
    table = Table(
        {
            "category": Vector(items=["A", "A", "A", "B", "B"], ray_type=Symbol),
            "type": Vector(items=["x", "x", "y", "x", "y"], ray_type=Symbol),
            "value": Vector(items=[10, 20, 30, 40, 50], ray_type=I64),
        }
    )

    result = table.pivot(index="category", columns="type", values="value", aggfunc="max").execute()

    # A has x: max(10,20)=20, y: 30; B has x: 40, y: 50
    result_dict = _get_pivot_values(result, "category")
    assert result_dict["A"]["x"] == 20
    assert result_dict["A"]["y"] == 30
    assert result_dict["B"]["x"] == 40
    assert result_dict["B"]["y"] == 50


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

    # A has x: first(10,20)=10, y: 30; B has x: 40, y: 50
    result_dict = _get_pivot_values(result, "category")
    assert result_dict["A"]["x"] == 10
    assert result_dict["A"]["y"] == 30
    assert result_dict["B"]["x"] == 40
    assert result_dict["B"]["y"] == 50


def test_pivot_with_last_aggfunc():
    table = Table(
        {
            "category": Vector(items=["A", "A", "A", "B", "B"], ray_type=Symbol),
            "type": Vector(items=["x", "x", "y", "x", "y"], ray_type=Symbol),
            "value": Vector(items=[10, 20, 30, 40, 50], ray_type=I64),
        }
    )

    result = table.pivot(index="category", columns="type", values="value", aggfunc="last").execute()

    # A has x: last(10,20)=20, y: 30; B has x: 40, y: 50
    result_dict = _get_pivot_values(result, "category")
    assert result_dict["A"]["x"] == 20
    assert result_dict["A"]["y"] == 30
    assert result_dict["B"]["x"] == 40
    assert result_dict["B"]["y"] == 50


def test_pivot_single_value_per_cell():
    table = Table(
        {
            "row": Vector(items=["r1", "r1", "r2", "r2"], ray_type=Symbol),
            "col": Vector(items=["c1", "c2", "c1", "c2"], ray_type=Symbol),
            "val": Vector(items=[1, 2, 3, 4], ray_type=I64),
        }
    )

    result = table.pivot(index="row", columns="col", values="val", aggfunc="min").execute()

    assert len(result) == 2
    columns = [str(c) for c in result.columns()]
    assert "c1" in columns
    assert "c2" in columns

    result_dict = _get_pivot_values(result, "row")
    assert result_dict["r1"]["c1"] == 1
    assert result_dict["r1"]["c2"] == 2
    assert result_dict["r2"]["c1"] == 3
    assert result_dict["r2"]["c2"] == 4


def test_pivot_preserves_order():
    table = Table(
        {
            "id": Vector(items=["a", "a", "a"], ray_type=Symbol),
            "key": Vector(items=["third", "first", "second"], ray_type=Symbol),
            "value": Vector(items=[3, 1, 2], ray_type=I64),
        }
    )

    result = table.pivot(index="id", columns="key", values="value", aggfunc="min").execute()

    # third, first, second
    columns = [str(c) for c in result.columns()]
    assert "third" in columns
    assert "first" in columns
    assert "second" in columns

    result_dict = _get_pivot_values(result, "id")
    assert result_dict["a"]["third"] == 3
    assert result_dict["a"]["first"] == 1
    assert result_dict["a"]["second"] == 2
