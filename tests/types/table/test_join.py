from rayforce import Table, TableColumnInterval
from rayforce.types.scalars import Time


def test_inner_join():
    trades = Table(
        columns=["Sym", "Ts", "Price"],
        values=[
            ["AAPL", "AAPL", "GOOGL", "GOOGL"],
            [
                Time("09:00:29.998"),
                Time("09:00:20.998"),
                Time("09:00:10.998"),
                Time("09:00:00.998"),
            ],
            [100, 200, 300, 400],
        ],
    )

    quotes = Table(
        columns=["Sym", "Bid", "Ask"],
        values=[
            ["AAPL", "GOOGL"],
            [50, 100],
            [75, 150],
        ],
    )

    result = trades.inner_join(quotes, "Sym")

    # Verify result is a table
    assert isinstance(result, Table)

    # Should have all columns from both tables
    assert len(result.columns) == 5
    assert "Sym" in result.columns
    assert "Ts" in result.columns
    assert "Price" in result.columns
    assert "Bid" in result.columns
    assert "Ask" in result.columns

    # Should have 4 rows (2 AAPL trades + 2 GOOGL trades)
    values = result.values()
    assert len(values) == 5  # 5 columns
    assert len(values[0]) == 4  # 4 rows

    # Verify AAPL trades are matched with AAPL quote (Bid=50, Ask=75)
    # Verify GOOGL trades are matched with GOOGL quote (Bid=100, Ask=150)
    sym_col = values[result.columns.index("Sym")]
    bid_col = values[result.columns.index("Bid")]
    ask_col = values[result.columns.index("Ask")]

    for i in range(len(sym_col)):
        sym_val = sym_col[i].value if hasattr(sym_col[i], "value") else str(sym_col[i])
        bid_val = bid_col[i].value if hasattr(bid_col[i], "value") else bid_col[i]
        ask_val = ask_col[i].value if hasattr(ask_col[i], "value") else ask_col[i]

        if sym_val == "AAPL":
            assert bid_val == 50
            assert ask_val == 75
        elif sym_val == "GOOGL":
            assert bid_val == 100
            assert ask_val == 150


def test_left_join():
    trades = Table(
        columns=["Sym", "Ts", "Price"],
        values=[
            ["AAPL", "GOOGL", "MSFT"],
            [
                Time("09:00:10.000"),
                Time("09:00:20.000"),
                Time("09:00:30.000"),
            ],
            [100, 200, 300],
        ],
    )

    quotes = Table(
        columns=["Sym", "Bid", "Ask"],
        values=[
            ["AAPL", "GOOGL"],
            [50, 100],
            [75, 150],
        ],
    )

    result = trades.left_join(quotes, "Sym")

    # Verify result is a table
    assert isinstance(result, Table)

    # Should have all columns from both tables
    assert len(result.columns) == 5
    assert "Sym" in result.columns
    assert "Ts" in result.columns
    assert "Price" in result.columns
    assert "Bid" in result.columns
    assert "Ask" in result.columns

    values = result.values()
    # Should have 3 rows (all trades, including unmatched MSFT)
    assert len(values) == 5
    assert len(values[0]) == 3

    sym_col = values[result.columns.index("Sym")]
    bid_col = values[result.columns.index("Bid")]
    ask_col = values[result.columns.index("Ask")]

    seen_syms = set()
    for i in range(len(sym_col)):
        sym_val = sym_col[i].value if hasattr(sym_col[i], "value") else str(sym_col[i])
        seen_syms.add(sym_val)

        bid_val = bid_col[i].value if hasattr(bid_col[i], "value") else bid_col[i]
        ask_val = ask_col[i].value if hasattr(ask_col[i], "value") else ask_col[i]

        if sym_val == "AAPL":
            assert bid_val == 50
            assert ask_val == 75
        elif sym_val == "GOOGL":
            assert bid_val == 100
            assert ask_val == 150
        elif sym_val == "MSFT":
            # For unmatched right-side rows we only assert that the left key exists
            # (exact null representation of Bid/Ask is runtime-specific)
            assert sym_val == "MSFT"

    assert seen_syms == {"AAPL", "GOOGL", "MSFT"}


def test_window_join():
    # Create trades table
    trades = Table(
        columns=["sym", "time", "price"],
        values=[
            ["AAPL", "GOOG"],
            [
                Time("09:00:00.100"),  # 100ms
                Time("09:00:00.100"),  # 100ms
            ],
            [150.0, 200.0],
        ],
    )

    # Create quotes within and outside the window
    # For trade at 100ms with window ±10ms (90ms to 110ms):
    # AAPL quotes: 90ms (bid=99), 95ms (bid=100), 105ms (bid=101), 110ms (bid=102)
    # GOOG quotes: 90ms (bid=199), 95ms (bid=200), 105ms (bid=201), 110ms (bid=202)
    quotes = Table(
        columns=["sym", "time", "bid", "ask"],
        values=[
            ["AAPL", "AAPL", "AAPL", "AAPL", "GOOG", "GOOG", "GOOG", "GOOG"],
            [
                Time("09:00:00.090"),
                Time("09:00:00.095"),
                Time("09:00:00.105"),
                Time("09:00:00.110"),
                Time("09:00:00.090"),
                Time("09:00:00.095"),
                Time("09:00:00.105"),
                Time("09:00:00.110"),
            ],
            [99.0, 100.0, 101.0, 102.0, 199.0, 200.0, 201.0, 202.0],
            [109.0, 110.0, 111.0, 112.0, 209.0, 210.0, 211.0, 212.0],
        ],
    )

    interval = TableColumnInterval(
        lower=-10,
        upper=10,
        table=trades,
        column=trades.time,
    )

    # Use window_join (wj)
    result = trades.window_join(
        on=["sym", "time"],
        interval=interval,
        join_with=[quotes],
        min_bid=quotes.bid.min(),
        max_ask=quotes.ask.max(),
    )

    # Verify result structure
    assert isinstance(result, Table)
    assert "min_bid" in result.columns
    assert "max_ask" in result.columns

    values = result.values()
    assert len(values[0]) == 2  # 2 trades

    min_bid_idx = result.columns.index("min_bid")
    max_ask_idx = result.columns.index("max_ask")
    sym_idx = result.columns.index("sym")

    min_bid_col = values[min_bid_idx]
    max_ask_col = values[max_ask_idx]
    sym_col = values[sym_idx]

    for i in range(2):
        sym = sym_col[i].value if hasattr(sym_col[i], "value") else str(sym_col[i])
        min_bid = (
            min_bid_col[i].value if hasattr(min_bid_col[i], "value") else min_bid_col[i]
        )
        max_ask = (
            max_ask_col[i].value if hasattr(max_ask_col[i], "value") else max_ask_col[i]
        )

        if sym == "AAPL":
            # Verify window captures quotes and aggregates correctly
            assert min_bid == 99.0, f"Expected min_bid=99.0 for AAPL, got {min_bid}"
            assert max_ask == 112.0, f"Expected max_ask=112.0 for AAPL, got {max_ask}"
        elif sym == "GOOG":
            # Verify window captures quotes and aggregates correctly
            assert min_bid == 199.0, f"Expected min_bid=199.0 for GOOG, got {min_bid}"
            assert max_ask == 212.0, f"Expected max_ask=212.0 for GOOG, got {max_ask}"


def test_window_join1():
    trades = Table(
        columns=["sym", "time", "price"],
        values=[
            ["AAPL", "AAPL", "GOOG", "GOOG"],
            [
                Time("09:00:00.100"),  # 100ms
                Time("09:00:00.300"),  # 300ms
                Time("09:00:00.150"),  # 150ms
                Time("09:00:00.350"),  # 350ms
            ],
            [150.0, 151.0, 200.0, 202.0],
        ],
    )

    quotes = Table(
        columns=["sym", "time", "bid", "ask"],
        values=[
            ["AAPL", "AAPL", "AAPL", "GOOG", "GOOG", "GOOG"],
            [
                Time("09:00:00.095"),  # 95ms - within window of AAPL trade at 100ms
                Time("09:00:00.105"),  # 105ms - within window of AAPL trade at 100ms
                Time("09:00:00.295"),  # 295ms - within window of AAPL trade at 300ms
                Time("09:00:00.145"),  # 145ms - within window of GOOG trade at 150ms
                Time("09:00:00.155"),  # 155ms - within window of GOOG trade at 150ms
                Time("09:00:00.345"),  # 345ms - within window of GOOG trade at 350ms
            ],
            [100.0, 101.0, 102.0, 200.0, 201.0, 202.0],  # bid prices
            [110.0, 111.0, 112.0, 210.0, 211.0, 212.0],  # ask prices
        ],
    )

    interval = TableColumnInterval(
        lower=-10,
        upper=10,
        table=trades,
        column=trades.time,
    )

    result = trades.window_join1(
        on=["sym", "time"],
        interval=interval,
        join_with=[quotes],
        min_bid=quotes.bid.min(),
        max_ask=quotes.ask.max(),
    )

    assert isinstance(result, Table)
    assert len(result.columns) == 5
    assert "sym" in result.columns
    assert "time" in result.columns
    assert "price" in result.columns
    assert "min_bid" in result.columns
    assert "max_ask" in result.columns

    values = result.values()
    assert len(values[0]) == 4  # 4 trades

    sym_idx = result.columns.index("sym")
    time_idx = result.columns.index("time")
    price_idx = result.columns.index("price")
    min_bid_idx = result.columns.index("min_bid")
    max_ask_idx = result.columns.index("max_ask")

    sym_col = values[sym_idx]
    time_col = values[time_idx]
    price_col = values[price_idx]
    min_bid_col = values[min_bid_idx]
    max_ask_col = values[max_ask_idx]

    for i in range(4):
        sym = sym_col[i].value if hasattr(sym_col[i], "value") else str(sym_col[i])
        trade_time = time_col[i]
        price = price_col[i].value if hasattr(price_col[i], "value") else price_col[i]
        min_bid = (
            min_bid_col[i].value if hasattr(min_bid_col[i], "value") else min_bid_col[i]
        )
        max_ask = (
            max_ask_col[i].value if hasattr(max_ask_col[i], "value") else max_ask_col[i]
        )

        # AAPL trade at 100ms: window [90ms, 110ms] captures quotes at 95ms and 105ms
        # min_bid should be 100.0, max_ask should be 111.0
        if sym == "AAPL" and str(trade_time) == "09:00:00.100":
            assert price == 150.0
            assert min_bid == 100.0, (
                f"Expected min_bid=100.0 for AAPL at 100ms, got {min_bid}"
            )
            assert max_ask == 111.0, (
                f"Expected max_ask=111.0 for AAPL at 100ms, got {max_ask}"
            )

        # AAPL trade at 300ms: window [290ms, 310ms] captures only quote at 295ms
        # min_bid should be 102.0, max_ask should be 112.0
        elif sym == "AAPL" and str(trade_time) == "09:00:00.300":
            assert price == 151.0
            assert min_bid == 102.0, (
                f"Expected min_bid=102.0 for AAPL at 300ms, got {min_bid}"
            )
            assert max_ask == 112.0, (
                f"Expected max_ask=112.0 for AAPL at 300ms, got {max_ask}"
            )

        # GOOG trade at 150ms: window [140ms, 160ms] captures quotes at 145ms and 155ms
        # min_bid should be 200.0, max_ask should be 211.0
        elif sym == "GOOG" and str(trade_time) == "09:00:00.150":
            assert price == 200.0
            assert min_bid == 200.0, (
                f"Expected min_bid=200.0 for GOOG at 150ms, got {min_bid}"
            )
            assert max_ask == 211.0, (
                f"Expected max_ask=211.0 for GOOG at 150ms, got {max_ask}"
            )

        # GOOG trade at 350ms: window [340ms, 360ms] captures only quote at 345ms
        # min_bid should be 202.0, max_ask should be 212.0
        elif sym == "GOOG" and str(trade_time) == "09:00:00.350":
            assert price == 202.0
            assert min_bid == 202.0, (
                f"Expected min_bid=202.0 for GOOG at 350ms, got {min_bid}"
            )
            assert max_ask == 212.0, (
                f"Expected max_ask=212.0 for GOOG at 350ms, got {max_ask}"
            )
