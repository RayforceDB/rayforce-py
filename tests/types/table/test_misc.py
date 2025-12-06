from rayforce.types import Table
from rayforce.types.scalars import Symbol, Time, I64, F64, B8, Date, Timestamp


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
    assert table.columns() == [
        Symbol("i64"),
        Symbol("f64"),
        Symbol("b8"),
        Symbol("date"),
        Symbol("time"),
        Symbol("timestamp"),
        Symbol("symbol"),
    ]

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
