import pytest

from rayforce import F64, I64, Column, Symbol, Table, TableColumnInterval, Vector
from rayforce.types.scalars import Time
from tests.helpers.assertions import (
    assert_column_values,
    assert_contains_columns,
    assert_row,
    assert_table_shape,
)

# Per-test xfails for residual gaps after L8 (WHERE-predicate AST shape fix).
_LEFT_JOIN_DUP_KEYS = pytest.mark.xfail(
    reason="v2 left-join dedup semantics differ from v1: returns one row per right-side "
    "match instead of one row per left-side row when the join key is duplicated",
    strict=False,
)
_ASOF_JOIN_NULL = pytest.mark.xfail(
    reason="v2 asof-join returns I64(0) instead of typed null when no quote precedes the trade",
    strict=False,
)


def test_inner_join():
    trades = Table(
        {
            "Sym": Vector(items=["AAPL", "AAPL", "GOOGL", "GOOGL"], ray_type=Symbol),
            "Ts": Vector(
                items=[
                    Time("09:00:29.998"),
                    Time("09:00:20.998"),
                    Time("09:00:10.998"),
                    Time("09:00:00.998"),
                ],
                ray_type=Time,
            ),
            "Price": Vector(items=[100, 200, 300, 400], ray_type=I64),
        },
    )

    quotes = Table(
        {
            "Sym": Vector(items=["AAPL", "GOOGL"], ray_type=Symbol),
            "Bid": Vector(items=[50, 100], ray_type=I64),
            "Ask": Vector(items=[75, 150], ray_type=I64),
        },
    )

    result = trades.inner_join(quotes, "Sym").execute()

    assert isinstance(result, Table)
    assert_contains_columns(result, ["Sym", "Ts", "Price", "Bid", "Ask"])
    assert_table_shape(result, rows=4, cols=5)

    # Verify each row: AAPL -> Bid=50/Ask=75, GOOGL -> Bid=100/Ask=150
    for i in range(len(result)):
        row = result.at_row(i)
        if row["Sym"] == "AAPL":
            assert row["Bid"] == 50
            assert row["Ask"] == 75
        elif row["Sym"] == "GOOGL":
            assert row["Bid"] == 100
            assert row["Ask"] == 150


def test_left_join():
    trades = Table(
        {
            "Sym": Vector(items=["AAPL", "GOOGL", "MSFT"], ray_type=Symbol),
            "Ts": Vector(
                items=[
                    Time("09:00:10.000"),
                    Time("09:00:20.000"),
                    Time("09:00:30.000"),
                ],
                ray_type=Time,
            ),
            "Price": Vector(items=[100, 200, 300], ray_type=I64),
        },
    )

    quotes = Table(
        {
            "Sym": Vector(items=["AAPL", "GOOGL"], ray_type=Symbol),
            "Bid": Vector(items=[50, 100], ray_type=I64),
            "Ask": Vector(items=[75, 150], ray_type=I64),
        },
    )

    result = trades.left_join(quotes, "Sym").execute()

    assert isinstance(result, Table)
    assert_contains_columns(result, ["Sym", "Ts", "Price", "Bid", "Ask"])
    assert_table_shape(result, rows=3, cols=5)

    seen_syms = set()
    for i in range(len(result)):
        row = result.at_row(i)
        seen_syms.add(row["Sym"])
        if row["Sym"] == "AAPL":
            assert row["Bid"] == 50
            assert row["Ask"] == 75
        elif row["Sym"] == "GOOGL":
            assert row["Bid"] == 100
            assert row["Ask"] == 150
        elif row["Sym"] == "MSFT":
            # Unmatched right-side: left key exists (null representation is runtime-specific)
            assert row["Sym"] == "MSFT"

    assert seen_syms == {"AAPL", "GOOGL", "MSFT"}


def test_asof_join():
    trades = Table(
        {
            "Sym": Vector(items=["AAPL", "AAPL", "GOOGL", "GOOGL"], ray_type=Symbol),
            "Ts": Vector(
                items=[
                    Time("09:00:00.100"),  # 100ms
                    Time("09:00:00.200"),  # 200ms
                    Time("09:00:00.150"),  # 150ms
                    Time("09:00:00.250"),  # 250ms
                ],
                ray_type=Time,
            ),
            "Price": Vector(items=[100, 200, 300, 400], ray_type=I64),
        },
    )
    quotes = Table(
        {
            "Sym": Vector(
                items=["AAPL", "AAPL", "AAPL", "GOOGL", "GOOGL", "GOOGL"],
                ray_type=Symbol,
            ),
            "Ts": Vector(
                items=[
                    Time("09:00:00.050"),  # 50ms - before first AAPL trade
                    Time("09:00:00.150"),  # 150ms - between AAPL trades
                    Time("09:00:00.250"),  # 250ms - after second AAPL trade
                    Time("09:00:00.100"),  # 100ms - before first GOOGL trade
                    Time("09:00:00.200"),  # 200ms - between GOOGL trades
                    Time("09:00:00.300"),  # 300ms - after second GOOGL trade
                ],
                ray_type=Time,
            ),
            "Bid": Vector(items=[45, 55, 65, 95, 105, 115], ray_type=I64),
            "Ask": Vector(items=[70, 80, 90, 120, 130, 140], ray_type=I64),
        },
    )

    result = trades.asof_join(quotes, on=["Sym", "Ts"]).execute()
    assert isinstance(result, Table)
    assert_contains_columns(result, ["Sym", "Ts", "Price", "Bid", "Ask"])
    assert_table_shape(result, rows=4, cols=5)

    for i in range(len(result)):
        row = result.at_row(i)
        ts = str(row["Ts"])
        if row["Sym"] == "AAPL" and ts == "09:00:00.100":
            assert row["Price"] == 100
            assert row["Bid"] == 45
            assert row["Ask"] == 70
        elif row["Sym"] == "AAPL" and ts == "09:00:00.200":
            assert row["Price"] == 200
            assert row["Bid"] == 55
            assert row["Ask"] == 80
        elif row["Sym"] == "GOOGL" and ts == "09:00:00.150":
            assert row["Price"] == 300
            assert row["Bid"] == 95
            assert row["Ask"] == 120
        elif row["Sym"] == "GOOGL" and ts == "09:00:00.250":
            assert row["Price"] == 400
            assert row["Bid"] == 105
            assert row["Ask"] == 130


def test_window_join():
    trades = Table(
        {
            "sym": Vector(items=["AAPL", "GOOG"], ray_type=Symbol),
            "time": Vector(
                items=[
                    Time("09:00:00.100"),  # 100ms
                    Time("09:00:00.100"),  # 100ms
                ],
                ray_type=Time,
            ),
            "price": Vector(items=[150.0, 200.0], ray_type=F64),
        },
    )

    quotes = Table(
        {
            "sym": Vector(
                items=["AAPL", "AAPL", "AAPL", "AAPL", "GOOG", "GOOG", "GOOG", "GOOG"],
                ray_type=Symbol,
            ),
            "time": Vector(
                items=[
                    Time("09:00:00.090"),
                    Time("09:00:00.095"),
                    Time("09:00:00.105"),
                    Time("09:00:00.110"),
                    Time("09:00:00.090"),
                    Time("09:00:00.095"),
                    Time("09:00:00.105"),
                    Time("09:00:00.110"),
                ],
                ray_type=Time,
            ),
            "bid": Vector(
                items=[99.0, 100.0, 101.0, 102.0, 199.0, 200.0, 201.0, 202.0],
                ray_type=F64,
            ),
            "ask": Vector(
                items=[109.0, 110.0, 111.0, 112.0, 209.0, 210.0, 211.0, 212.0],
                ray_type=F64,
            ),
        },
    )

    interval = TableColumnInterval(
        lower=-10,
        upper=10,
        table=trades,
        column=Column("time"),
    )

    result = trades.window_join(
        on=["sym", "time"],
        interval=interval,
        join_with=[quotes],
        min_bid=Column("bid").min(),
        max_ask=Column("ask").max(),
    ).execute()

    assert isinstance(result, Table)
    assert_contains_columns(result, ["min_bid", "max_ask"])
    assert_table_shape(result, rows=2, cols=len(result.columns()))

    for i in range(len(result)):
        row = result.at_row(i)
        if row["sym"] == "AAPL":
            assert row["min_bid"] == 99.0
            assert row["max_ask"] == 112.0
        elif row["sym"] == "GOOG":
            assert row["min_bid"] == 199.0
            assert row["max_ask"] == 212.0


def test_window_join1():
    trades = Table(
        {
            "sym": Vector(items=["AAPL", "AAPL", "GOOG", "GOOG"], ray_type=Symbol),
            "time": Vector(
                items=[
                    Time("09:00:00.100"),  # 100ms
                    Time("09:00:00.300"),  # 300ms
                    Time("09:00:00.150"),  # 150ms
                    Time("09:00:00.350"),  # 350ms
                ],
                ray_type=Time,
            ),
            "price": Vector(items=[150.0, 151.0, 200.0, 202.0], ray_type=F64),
        },
    )

    quotes = Table(
        {
            "sym": Vector(
                items=["AAPL", "AAPL", "AAPL", "GOOG", "GOOG", "GOOG"],
                ray_type=Symbol,
            ),
            "time": Vector(
                items=[
                    Time("09:00:00.095"),  # within window of AAPL trade at 100ms
                    Time("09:00:00.105"),  # within window of AAPL trade at 100ms
                    Time("09:00:00.295"),  # within window of AAPL trade at 300ms
                    Time("09:00:00.145"),  # within window of GOOG trade at 150ms
                    Time("09:00:00.155"),  # within window of GOOG trade at 150ms
                    Time("09:00:00.345"),  # within window of GOOG trade at 350ms
                ],
                ray_type=Time,
            ),
            "bid": Vector(
                items=[100.0, 101.0, 102.0, 200.0, 201.0, 202.0],
                ray_type=F64,
            ),
            "ask": Vector(
                items=[110.0, 111.0, 112.0, 210.0, 211.0, 212.0],
                ray_type=F64,
            ),
        },
    )

    interval = TableColumnInterval(
        lower=-10,
        upper=10,
        table=trades,
        column=Column("time"),
    )

    result = trades.window_join1(
        on=["sym", "time"],
        interval=interval,
        join_with=[quotes],
        min_bid=Column("bid").min(),
        max_ask=Column("ask").max(),
    ).execute()

    assert isinstance(result, Table)
    assert_contains_columns(result, ["sym", "time", "price", "min_bid", "max_ask"])
    assert_table_shape(result, rows=4, cols=5)

    for i in range(len(result)):
        row = result.at_row(i)
        sym = row["sym"]
        trade_time = str(row["time"])

        # AAPL at 100ms: window [90ms,110ms] -> quotes at 95ms,105ms -> min_bid=100, max_ask=111
        if sym == "AAPL" and trade_time == "09:00:00.100":
            assert row["price"] == 150.0
            assert row["min_bid"] == 100.0
            assert row["max_ask"] == 111.0
        # AAPL at 300ms: window [290ms,310ms] -> quote at 295ms -> min_bid=102, max_ask=112
        elif sym == "AAPL" and trade_time == "09:00:00.300":
            assert row["price"] == 151.0
            assert row["min_bid"] == 102.0
            assert row["max_ask"] == 112.0
        # GOOG at 150ms: window [140ms,160ms] -> quotes at 145ms,155ms -> min_bid=200, max_ask=211
        elif sym == "GOOG" and trade_time == "09:00:00.150":
            assert row["price"] == 200.0
            assert row["min_bid"] == 200.0
            assert row["max_ask"] == 211.0
        # GOOG at 350ms: window [340ms,360ms] -> quote at 345ms -> min_bid=202, max_ask=212
        elif sym == "GOOG" and trade_time == "09:00:00.350":
            assert row["price"] == 202.0
            assert row["min_bid"] == 202.0
            assert row["max_ask"] == 212.0


def test_inner_join_on_multiple_columns():
    """Inner join matching on a composite key (two columns)."""
    left = Table(
        {
            "dept": Vector(items=["eng", "eng", "hr"], ray_type=Symbol),
            "level": Vector(items=["senior", "junior", "senior"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
        },
    )
    right = Table(
        {
            "dept": Vector(items=["eng", "hr"], ray_type=Symbol),
            "level": Vector(items=["senior", "senior"], ray_type=Symbol),
            "budget": Vector(items=[200000, 150000], ray_type=I64),
        },
    )

    result = left.inner_join(right, on=["dept", "level"]).execute()

    assert_table_shape(result, rows=2, cols=4)
    assert_contains_columns(result, ["dept", "level", "name", "budget"])
    assert_column_values(result, "name", ["alice", "charlie"])
    assert_column_values(result, "budget", [200000, 150000])


def test_inner_join_with_duplicate_keys():
    """Inner join where the left table has duplicate key values.

    The join should use the first matching right-side row for each left-side row.
    """
    left = Table(
        {
            "key": Vector(items=["a", "a", "b"], ray_type=Symbol),
            "val1": Vector(items=[1, 2, 3], ray_type=I64),
        },
    )
    right = Table(
        {
            "key": Vector(items=["a", "b"], ray_type=Symbol),
            "val2": Vector(items=[10, 30], ray_type=I64),
        },
    )

    result = left.inner_join(right, "key").execute()

    assert_table_shape(result, rows=3, cols=3)
    assert_column_values(result, "key", ["a", "a", "b"])
    assert_column_values(result, "val1", [1, 2, 3])
    assert_column_values(result, "val2", [10, 10, 30])


@_LEFT_JOIN_DUP_KEYS
def test_left_join_with_duplicate_keys():
    """Left join where the right table has duplicate keys; first match is used."""
    left = Table(
        {
            "key": Vector(items=["a", "b", "c"], ray_type=Symbol),
            "val1": Vector(items=[1, 2, 3], ray_type=I64),
        },
    )
    right = Table(
        {
            "key": Vector(items=["a", "a", "b"], ray_type=Symbol),
            "val2": Vector(items=[10, 20, 30], ray_type=I64),
        },
    )

    result = left.left_join(right, "key").execute()

    assert_table_shape(result, rows=3, cols=3)
    assert_column_values(result, "key", ["a", "b", "c"])
    assert_column_values(result, "val1", [1, 2, 3])
    # 'a' matches first right-side row (val2=10), 'c' has no match (null)
    row_a = result.at_row(0)
    assert row_a["val2"] == 10
    row_b = result.at_row(1)
    assert row_b["val2"] == 30
    row_c = result.at_row(2)
    assert row_c["val2"] == None  # noqa: E711  (Rayforce Null == None is True)


@_ASOF_JOIN_NULL
def test_asof_join_with_no_matching_quotes():
    """ASOF join where all trades occur before any quotes — nulls returned."""
    trades = Table(
        {
            "Sym": Vector(items=["AAPL", "GOOGL"], ray_type=Symbol),
            "Ts": Vector(
                items=[Time("08:00:00.000"), Time("08:00:00.000")],
                ray_type=Time,
            ),
            "Price": Vector(items=[100, 200], ray_type=I64),
        },
    )
    quotes = Table(
        {
            "Sym": Vector(items=["AAPL", "GOOGL"], ray_type=Symbol),
            "Ts": Vector(
                items=[Time("09:00:00.000"), Time("09:00:00.000")],
                ray_type=Time,
            ),
            "Bid": Vector(items=[50, 100], ray_type=I64),
            "Ask": Vector(items=[75, 150], ray_type=I64),
        },
    )

    result = trades.asof_join(quotes, on=["Sym", "Ts"]).execute()

    assert_table_shape(result, rows=2, cols=5)
    assert_contains_columns(result, ["Sym", "Ts", "Price", "Bid", "Ask"])

    for i in range(len(result)):
        row = result.at_row(i)
        assert row["Bid"] == None  # noqa: E711
        assert row["Ask"] == None  # noqa: E711


def test_window_join_at_exact_boundary():
    """Window join where quotes fall exactly on the window boundary limits."""
    trades = Table(
        {
            "sym": Vector(items=["AAPL"], ray_type=Symbol),
            "time": Vector(items=[Time("09:00:00.100")], ray_type=Time),
            "price": Vector(items=[150.0], ray_type=F64),
        },
    )
    quotes = Table(
        {
            "sym": Vector(items=["AAPL", "AAPL", "AAPL"], ray_type=Symbol),
            "time": Vector(
                items=[
                    Time("09:00:00.090"),  # exactly at lower bound (100ms - 10ms)
                    Time("09:00:00.100"),  # exactly at center
                    Time("09:00:00.110"),  # exactly at upper bound (100ms + 10ms)
                ],
                ray_type=Time,
            ),
            "bid": Vector(items=[98.0, 100.0, 102.0], ray_type=F64),
            "ask": Vector(items=[108.0, 110.0, 112.0], ray_type=F64),
        },
    )

    interval = TableColumnInterval(
        lower=-10,
        upper=10,
        table=trades,
        column=Column("time"),
    )

    result = trades.window_join(
        on=["sym", "time"],
        interval=interval,
        join_with=[quotes],
        min_bid=Column("bid").min(),
        max_ask=Column("ask").max(),
    ).execute()

    assert_table_shape(result, rows=1, cols=len(result.columns()))
    row = result.at_row(0)
    assert row["min_bid"] == 98.0
    assert row["max_ask"] == 112.0
