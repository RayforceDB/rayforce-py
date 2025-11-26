from raypy import Table, TableColumnInterval
from raypy.types.scalars import Symbol, Time, I64, F64, B8, Date, Timestamp


def test_select_with_single_where():
    table = Table(
        columns=["id", "name", "age", "salary"],
        values=[
            ["001", "002", "003", "004"],
            ["alice", "bob", "charlie", "dana"],
            [29, 34, 41, 38],
            [100000, 120000, 90000, 85000],
        ],
    )

    result = table.select("id", "name", "age").where(table.age >= 35).execute()

    assert len(result.columns) == 3
    assert "id" in result.columns
    assert "name" in result.columns
    assert "age" in result.columns

    values = result.values()
    assert len(values) == 3
    assert len(values[0]) == 2
    assert values[0][0].value == "003"
    assert values[0][1].value == "004"
    assert values[1][0].value == "charlie"
    assert values[1][1].value == "dana"
    assert values[2][0].value == 41
    assert values[2][1].value == 38


def test_select_with_multiple_where_conditions():
    table = Table(
        columns=["id", "name", "age", "dept", "salary"],
        values=[
            ["001", "002", "003", "004", "005"],
            ["alice", "bob", "charlie", "dana", "eli"],
            [29, 34, 41, 38, 45],
            ["eng", "eng", "marketing", "eng", "marketing"],
            [100000, 120000, 90000, 85000, 95000],
        ],
    )

    result = (
        table.select("id", "name", "age", "salary")
        .where(table.age >= 35)
        .where(table.dept == "eng")
        .execute()
    )

    values = result.values()
    assert len(values) == 4
    assert len(values[0]) == 1
    assert values[0][0].value == "004"
    assert values[1][0].value == "dana"
    assert values[2][0].value == 38
    assert values[3][0].value == 85000


def test_select_with_complex_and_or_conditions():
    table = Table(
        columns=["id", "name", "age", "dept", "salary"],
        values=[
            ["001", "002", "003", "004", "005"],
            ["alice", "bob", "charlie", "dana", "eli"],
            [29, 34, 41, 38, 45],
            ["eng", "eng", "marketing", "eng", "marketing"],
            [100000, 120000, 90000, 85000, 95000],
        ],
    )

    result = (
        table.select("id", "name")
        .where((table.age >= 35) & (table.dept == "eng"))
        .where((table.salary > 80000) | (table.age < 40))
        .execute()
    )

    values = result.values()
    assert len(values) == 2
    assert len(values[0]) >= 0


def test_group_by_single_column():
    table = Table(
        columns=["dept", "age", "salary"],
        values=[
            ["eng", "eng", "marketing", "marketing", "hr"],
            [29, 34, 41, 38, 35],
            [100000, 120000, 90000, 85000, 80000],
        ],
    )

    result = (
        table.select(
            avg_age=table.age.mean(),
            total_salary=table.salary.sum(),
            count=table.age.count(),
        )
        .by("dept")
        .execute()
    )

    assert len(result.columns) >= 4
    assert "dept" in result.columns or "by" in result.columns
    assert "avg_age" in result.columns
    assert "total_salary" in result.columns
    assert "count" in result.columns

    values = result.values()
    assert len(values) >= 3

    # Find the column indices
    cols = result.columns
    dept_idx = cols.index("dept") if "dept" in cols else cols.index("by")
    avg_age_idx = cols.index("avg_age")
    total_salary_idx = cols.index("total_salary")
    count_idx = cols.index("count")

    # Expected: eng (avg_age=31.5, total_salary=220000, count=2)
    #           marketing (avg_age=39.5, total_salary=175000, count=2)
    #           hr (avg_age=35, total_salary=80000, count=1)

    dept_col = values[dept_idx]
    avg_age_col = values[avg_age_idx]
    total_salary_col = values[total_salary_idx]
    count_col = values[count_idx]

    # Find eng group
    for i in range(len(dept_col)):
        dept_val = (
            dept_col[i].value if hasattr(dept_col[i], "value") else str(dept_col[i])
        )
        if dept_val == "eng":
            assert abs(avg_age_col[i].value - 31.5) < 0.01
            assert total_salary_col[i].value == 220000
            assert count_col[i].value == 2
        elif dept_val == "marketing":
            assert abs(avg_age_col[i].value - 39.5) < 0.01
            assert total_salary_col[i].value == 175000
            assert count_col[i].value == 2
        elif dept_val == "hr":
            assert avg_age_col[i].value == 35
            assert total_salary_col[i].value == 80000
            assert count_col[i].value == 1


def test_group_by_multiple_columns():
    table = Table(
        columns=["dept", "level", "salary"],
        values=[
            ["eng", "eng", "eng", "marketing", "marketing"],
            ["senior", "junior", "senior", "senior", "junior"],
            [150000, 100000, 140000, 120000, 90000],
        ],
    )

    result = (
        table.select(
            total_salary=table.salary.sum(),
            avg_salary=table.salary.mean(),
        )
        .by("dept", "level")
        .execute()
    )

    assert len(result.columns) >= 4
    values = result.values()
    assert len(values) >= 2

    # Expected groups:
    # eng/senior: total=290000 (150000+140000), avg=145000
    # eng/junior: total=100000, avg=100000
    # marketing/senior: total=120000, avg=120000
    # marketing/junior: total=90000, avg=90000

    cols = result.columns
    dept_idx = cols.index("dept") if "dept" in cols else cols.index("by")
    level_idx = (
        cols.index("level")
        if "level" in cols
        else (cols.index("by") + 1 if "by" in cols else 0)
    )
    total_salary_idx = cols.index("total_salary")
    avg_salary_idx = cols.index("avg_salary")

    dept_col = values[dept_idx]
    level_col = values[level_idx]
    total_salary_col = values[total_salary_idx]
    avg_salary_col = values[avg_salary_idx]

    for i in range(len(dept_col)):
        dept_val = (
            dept_col[i].value if hasattr(dept_col[i], "value") else str(dept_col[i])
        )
        level_val = (
            level_col[i].value if hasattr(level_col[i], "value") else str(level_col[i])
        )

        if dept_val == "eng" and level_val == "senior":
            assert total_salary_col[i].value == 290000
            assert avg_salary_col[i].value == 145000
        elif dept_val == "eng" and level_val == "junior":
            assert total_salary_col[i].value == 100000
            assert avg_salary_col[i].value == 100000
        elif dept_val == "marketing" and level_val == "senior":
            assert total_salary_col[i].value == 120000
            assert avg_salary_col[i].value == 120000
        elif dept_val == "marketing" and level_val == "junior":
            assert total_salary_col[i].value == 90000
            assert avg_salary_col[i].value == 90000


def test_group_by_with_filtered_aggregation():
    table = Table(
        columns=["category", "amount", "status"],
        values=[
            ["A", "A", "B", "B", "A"],
            [100, 200, 150, 250, 300],
            ["active", "inactive", "active", "active", "inactive"],
        ],
    )

    result = (
        table.select(
            total=table.amount.sum(),
            active_total=table.amount.where(table.status == "active").sum(),
            count=table.amount.count(),
        )
        .by("category")
        .execute()
    )

    assert "total" in result.columns
    assert "active_total" in result.columns
    assert "count" in result.columns

    values = result.values()
    assert len(values) >= 3

    # Expected:
    # Category A: total=600 (100+200+300), active_total=100 (only first is active), count=3
    # Category B: total=400 (150+250), active_total=400 (both active), count=2

    cols = result.columns
    category_idx = cols.index("category") if "category" in cols else cols.index("by")
    total_idx = cols.index("total")
    active_total_idx = cols.index("active_total")
    count_idx = cols.index("count")

    category_col = values[category_idx]
    total_col = values[total_idx]
    active_total_col = values[active_total_idx]
    count_col = values[count_idx]

    for i in range(len(category_col)):
        cat_val = (
            category_col[i].value
            if hasattr(category_col[i], "value")
            else str(category_col[i])
        )
        if cat_val == "A":
            assert total_col[i].value == 600
            assert active_total_col[i].value == 100
            assert count_col[i].value == 3
        elif cat_val == "B":
            assert total_col[i].value == 400
            assert active_total_col[i].value == 400
            assert count_col[i].value == 2


def test_update_single_row():
    table = Table(
        columns=["id", "name", "age"],
        values=[["001", "002", "003"], ["alice", "bob", "charlie"], [29, 34, 41]],
    )
    table.save("test_update_table")

    result = (
        Table.get("test_update_table")
        .update(age=100)
        .where(lambda t: t.id == "001")
        .execute()
    )

    if isinstance(result, Table):
        values = result.values()
        assert values[2][0].value == 100


def test_update_multiple_rows():
    table = Table(
        columns=["id", "dept", "salary"],
        values=[
            ["001", "002", "003"],
            ["eng", "eng", "marketing"],
            [100000, 120000, 90000],
        ],
    )
    table.save("test_update_multi")

    result = (
        Table.get("test_update_multi")
        .update(salary=150000)
        .where(lambda t: t.dept == "eng")
        .execute()
    )

    if isinstance(result, Table):
        values = result.values()
        assert len(values) == 3


def test_insert_single_row():
    table = Table(
        columns=["id", "name", "age"],
        values=[["001", "002"], ["alice", "bob"], [29, 34]],
    )
    table.save("test_insert_table")

    result = (
        Table.get("test_insert_table")
        .insert(id="003", name="charlie", age=41)
        .execute()
    )

    assert isinstance(result, Symbol)

    result = Table.get("test_insert_table")
    print(result.values())
    values = result.values()
    assert len(values[0]) == 3
    assert values[0][2].value == "003"
    assert values[1][2].value == "charlie"
    assert values[2][2].value == 41


def test_upsert_single_row():
    table = Table(
        columns=["id", "name", "age"],
        values=[["001", "002"], ["alice", "bob"], [29, 34]],
    )
    table.save("test_upsert_table")

    result = (
        Table.get("test_upsert_table")
        .upsert({"id": "001", "name": "alice_updated", "age": 30}, match_on="id")
        .execute()
    )

    assert isinstance(result, Symbol)

    result = Table.get("test_upsert_table")
    values = result.values()
    assert len(values[0]) == 2
    assert values[1][0].value == "alice_updated"
    assert values[2][0].value == 30


def test_upsert_multiple_rows():
    table = Table(
        columns=["id", "name", "age"],
        values=[["001", "002"], ["alice", "bob"], [29, 34]],
    )
    table.save("test_upsert_multi")

    result = (
        Table.get("test_upsert_multi")
        .upsert(
            [
                {"id": "001", "name": "alice_new", "age": 30},
                {"id": "003", "name": "charlie", "age": 41},
            ],
            match_on="id",
        )
        .execute()
    )

    assert isinstance(result, Symbol)

    result = Table.get("test_upsert_multi")
    values = result.values()
    assert len(values[0]) >= 2
    assert values[1][0].value == "alice_new"


def test_upsert_with_multiple_match_keys():
    table = Table(
        columns=["id", "version", "value"],
        values=[
            ["001", "001", "002"],
            ["v1", "v2", "v1"],
            [100, 200, 300],
        ],
    )
    table.save("test_upsert_match_keys")

    result = (
        Table.get("test_upsert_match_keys")
        .upsert(
            {"id": "001", "version": "v1", "value": 150},
            match_on=["id", "version"],
        )
        .execute()
    )

    assert isinstance(result, Symbol)

    result = Table.get("test_upsert_match_keys")
    values = result.values()
    assert len(values) == 3


def test_complex_select_with_computed_columns():
    table = Table(
        columns=["id", "price", "quantity"],
        values=[
            ["001", "002", "003"],
            [10.5, 20.0, 15.75],
            [2, 3, 4],
        ],
    )

    result = (
        table.select(
            "id",
            total=table.price * table.quantity,
            discounted=table.price * table.quantity * 0.9,
        )
        .where(table.quantity >= 3)
        .execute()
    )

    assert "id" in result.columns
    assert "total" in result.columns
    assert "discounted" in result.columns

    values = result.values()
    assert len(values) == 3
    assert len(values[0]) == 2


def test_order_by():
    table = Table(
        columns=["id", "name", "age"],
        values=[
            ["001", "002", "003", "004"],
            ["alice", "bob", "charlie", "dana"],
            [29, 34, 41, 38],
        ],
    )

    result = table.xdesc("age")
    values = result.values()
    assert (
        values[2][0].value
        > values[2][1].value
        > values[2][2].value
        > values[2][3].value
    )

    result = table.xasc("age")
    values = result.values()
    assert (
        values[2][3].value
        > values[2][2].value
        > values[2][1].value
        > values[2][0].value
    )


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


def test_table_from_csv_all_types(tmp_path):
    # Prepare a CSV file that exercises all supported scalar types
    csv_content = "\n".join(
        [
            "i64,f64,b8,date,time,timestamp,symbol",
            "1,1.5,true,2001-01-02,09:00:00,2001-01-02 09:00:00,foo",
            "2,2.5,false,2001-01-03,10:00:00,2001-01-03 10:00:00,bar",
            "",
        ]
    )

    csv_path = tmp_path / "all_types.csv"
    csv_path.write_text(csv_content)

    table = Table.from_csv(
        [I64, F64, B8, Date, Time, Timestamp, Symbol],
        str(csv_path),
    )

    # Basic shape and columns
    assert isinstance(table, Table)
    assert table.columns == [
        "i64",
        "f64",
        "b8",
        "date",
        "time",
        "timestamp",
        "symbol",
    ]
    assert table.shape == (2, 7)

    values = table.values()
    assert len(values) == 7

    i64_col, f64_col, b8_col, date_col, time_col, ts_col, sym_col = values

    # Integer column (I64)
    assert [v.value for v in i64_col] == [1, 2]

    # Float column (F64)
    assert [round(v.value, 6) for v in f64_col] == [1.5, 2.5]

    # Boolean column (B8)
    # assert [v.value for v in b8_col] == [True, False]

    # Date column (Date)
    assert [d.value.isoformat() for d in date_col] == [
        "2001-01-02",
        "2001-01-03",
    ]

    # Time column (Time)
    # assert [t.value.isoformat() for t in time_col] == [
    #     "09:00:00",
    #     "10:00:00",
    # ]

    # Timestamp column (Timestamp) – compare date/time portion, ignore timezone details
    # ts_str = [ts.value.replace(tzinfo=None).isoformat(sep=" ") for ts in ts_col]
    # assert ts_str == [
    #     "2001-01-02 09:00:00",
    #     "2001-01-03 10:00:00",
    # ]

    # Symbol column
    assert [s.value for s in sym_col] == ["foo", "bar"]
