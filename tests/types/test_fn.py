from rayforce import I64, Column, Fn, Symbol, Table, Vector


def test_fn_direct_call_scalar():
    square = Fn("(fn [x] (* x x))")
    result = square(5)
    assert result == 25
    result = square(10)
    assert result == 100


def test_fn_direct_call_multiple_args():
    add = Fn("(fn [x y] (+ x y))")
    result = add(5, 3)
    assert result == 8
    result = add(10, 20)
    assert result == 30


def test_fn_fibonacci_direct_call():
    fib = Fn("(fn [x] (if (< x 2) 1 (+ (self (- x 1)) (self (- x 2)))))")

    assert fib(0) == 1
    assert fib(1) == 1
    assert fib(2) == 2
    assert fib(3) == 3
    assert fib(4) == 5


def test_fn_apply_to_column():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "value": Vector(items=[2, 3, 4], ray_type=I64),
        },
    )

    square = Fn("(fn [x] (* x x))")

    result = table.select(
        "id",
        squared_value=square.apply(Column("value")),
    ).execute()

    columns = result.columns()
    assert "id" in columns
    assert "squared_value" in columns

    squared_values = result.at_column("squared_value")

    assert squared_values[0].value == 4
    assert squared_values[1].value == 9
    assert squared_values[2].value == 16


def test_fn_apply_with_aggregation():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "value": Vector(items=[2, 3, 4, 5], ray_type=I64),
        },
    )

    square = Fn("(fn [x] (* x x))")

    result = table.select(
        sum_of_squares=square.apply(Column("value")).sum(),
        avg_of_squares=square.apply(Column("value")).mean(),
        max_of_squares=square.apply(Column("value")).max(),
    ).execute()

    columns = result.columns()
    assert "sum_of_squares" in columns
    assert "avg_of_squares" in columns
    assert "max_of_squares" in columns

    values = result.values()
    assert values[0][0].value == 54
    assert values[1][0].value == 13.5
    assert values[2][0].value == 25


def test_fn_apply_with_group_by():
    table = Table(
        {
            "category": Vector(items=["A", "A", "B", "B"], ray_type=Symbol),
            "value": Vector(items=[2, 3, 4, 5], ray_type=I64),
        },
    )

    square = Fn("(fn [x] (* x x))")

    result = (
        table.select(
            sum_of_squares=square.apply(Column("value")).sum(),
        )
        .by("category")
        .execute()
    )

    columns = result.columns()
    assert "category" in columns
    assert "sum_of_squares" in columns

    values = result.values()
    assert len(values[0]) == 2
    assert values[1][0].value == 13 or values[1][0].value == 41
    assert values[1][1].value == 13 or values[1][1].value == 41


def test_fn_normalize_with_multiple_args():
    table = Table(
        {
            "value": Vector(items=[50, 75, 100], ray_type=I64),
            "min_val": Vector(items=[0, 0, 0], ray_type=I64),
            "max_val": Vector(items=[100, 100, 100], ray_type=I64),
        },
    )

    normalize = Fn("(fn [x min_val max_val] (/ (- x min_val) (- max_val min_val)))")

    result = table.select(
        "value",
        normalized=normalize.apply(
            Column("value"),
            Column("min_val"),
            Column("max_val"),
        ),
    ).execute()

    columns = result.columns()
    assert "value" in columns
    assert "normalized" in columns

    values = result.values()
    normalized_values = values[1]

    assert normalized_values[0].value == 0  # (50 - 0) / (100 - 0)
    assert normalized_values[1].value == 0  # (75 - 0) / (100 - 0)
    assert normalized_values[2].value == 1  # (100 - 0) / (100 - 0)


def test_fn_fibonacci_with_aggregation():
    table = Table(
        {
            "group": Vector(items=["A", "A", "B", "B"], ray_type=Symbol),
            "n": Vector(items=[0, 1, 2, 3], ray_type=I64),
        },
    )

    fib = Fn("(fn [x] (if (< x 2) 1 (+ (self (- x 1)) (self (- x 2)))))")

    result = (
        table.select(
            fib_sum=fib.apply(Column("n")).sum(),
            fib_max=fib.apply(Column("n")).max(),
            fib_count=fib.apply(Column("n")).count(),
        )
        .by("group")
        .execute()
    )

    columns = result.columns()
    assert "group" in columns
    assert "fib_sum" in columns
    assert "fib_max" in columns
    assert "fib_count" in columns

    values = result.values()
    # Group A: n=[0,1] -> fib=[1,1] -> sum=2, max=1, count=2
    # Group B: n=[2,3] -> fib=[2,3] -> sum=5, max=3, count=2
    assert len(values[0]) == 2  # Two groups


def test_fn_complex_expression():
    table = Table(
        {
            "x": Vector(items=[2, 3, 4], ray_type=I64),
            "y": Vector(items=[3, 4, 5], ray_type=I64),
        },
    )

    sum_squares = Fn("(fn [x y] (+ (* x x) (* y y)))")

    result = table.select(
        "x",
        "y",
        sum_of_squares=sum_squares.apply(Column("x"), Column("y")),
    ).execute()

    columns = result.columns()
    assert "x" in columns
    assert "y" in columns
    assert "sum_of_squares" in columns

    values = result.values()
    sum_values = values[2]

    assert sum_values[0].value == 13  # 2^2 + 3^2 = 4 + 9
    assert sum_values[1].value == 25  # 3^2 + 4^2 = 9 + 16
    assert sum_values[2].value == 41  # 4^2 + 5^2 = 16 + 25


def test_fn_conditional_lambda():
    table = Table(
        {
            "value": Vector(items=[-5, 0, 5, 10], ray_type=I64),
        },
    )

    # Lambda that returns absolute value
    abs_fn = Fn("(fn [x] (if (< x 0) (* -1 x) x))")

    result = table.select(
        "value",
        abs_value=abs_fn.apply(Column("value")),
    ).execute()

    columns = result.columns()
    assert "value" in columns
    assert "abs_value" in columns

    values = result.values()
    abs_values = values[1]

    assert abs_values[0].value == 5  # abs(-5)
    assert abs_values[1].value == 0  # abs(0)
    assert abs_values[2].value == -5  # abs(5)
    assert abs_values[3].value == -10  # abs(10)


def test_fn_with_where_clause():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "value": Vector(items=[2, 3, 4, 5], ray_type=I64),
        },
    )

    square = Fn("(fn [x] (* x x))")

    result = (
        table.select(
            "id",
            squared_value=square.apply(Column("value")),
        )
        .where(Column("value") > 3)
        .execute()
    )

    columns = result.columns()
    assert "id" in columns
    assert "squared_value" in columns

    values = result.values()
    # Should only have rows where value > 3 (4 and 5)
    assert len(values[0]) == 2
    assert values[1][0].value == 16  # 4^2
    assert values[1][1].value == 25  # 5^2
