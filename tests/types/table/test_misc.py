import pytest
from rayforce.types import Table, Vector, Column
from rayforce.types.scalars import Symbol, Time, I64, F64, B8, Date, Timestamp
from rayforce.types.exceptions import PartedTableError


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
    assert [v.value for v in b8_col] == [True, False]

    # Date column (Date)
    assert [d.value.isoformat() for d in date_col] == [
        "2001-01-02",
        "2001-01-03",
    ]

    # Time column (Time)
    # TODO: CSV parser doesn't properly support Time type yet
    # assert [t.value.isoformat() for t in time_col] == [
    #     "09:00:00",
    #     "10:00:00",
    # ]

    # Timestamp column (Timestamp) – compare date/time portion, ignore timezone details
    ts_str = [ts.value.replace(tzinfo=None).isoformat(sep=" ") for ts in ts_col]
    assert ts_str == [
        "2001-01-02 09:00:00",
        "2001-01-03 10:00:00",
    ]

    # Symbol column
    assert [s.value for s in sym_col] == ["foo", "bar"]


def test_set_splayed_and_from_splayed(tmp_path):
    table = Table.from_dict(
        {
            "category": Vector(items=["A", "B", "A", "B"], ray_type=Symbol),
            "amount": Vector(items=[100, 200, 150, 250], ray_type=I64),
            "status": Vector(items=["active", "inactive", "active", "active"], ray_type=Symbol),
        }
    )

    splayed_dir = tmp_path / "test_splayed"
    splayed_dir.mkdir()

    table.set_splayed(f"{splayed_dir}/")

    assert splayed_dir.exists()
    assert (splayed_dir / ".d").exists()
    assert (splayed_dir / "category").exists()
    assert (splayed_dir / "amount").exists()
    assert (splayed_dir / "status").exists()

    loaded_table = Table.from_splayed(f"{splayed_dir}/")

    assert isinstance(loaded_table, Table)
    columns = loaded_table.columns()
    assert len(columns) == 3
    assert Symbol("category") in columns
    assert Symbol("amount") in columns
    assert Symbol("status") in columns

    values = loaded_table.select("*").execute().values()
    assert len(values) == 3

    category_col, amount_col, status_col = values
    assert [s.value for s in category_col] == ["A", "B", "A", "B"]
    assert [v.value for v in amount_col] == [100, 200, 150, 250]
    assert [s.value for s in status_col] == ["active", "inactive", "active", "active"]


def test_set_splayed_and_from_parted(tmp_path):
    table = Table.from_dict(
        {
            "category": Vector(items=["A", "B", "C", "D"], ray_type=Symbol),
            "amount": Vector(items=[100, 200, 150, 250], ray_type=I64),
            "status": Vector(items=["active", "inactive", "active", "active"], ray_type=Symbol),
        }
    )

    splayed_dir = tmp_path / "test_splayed"
    splayed_dir.mkdir()
    assert splayed_dir.exists()

    for i in ["2024.01.01", "2024.01.02", "2024.01.03"]:
        table.set_splayed(f"{splayed_dir}/{i}/test/", f"{splayed_dir}/sym")

        assert (splayed_dir / f"{i}" / "test" / ".d").exists()
        assert (splayed_dir / f"{i}" / "test" / "category").exists()
        assert (splayed_dir / f"{i}" / "test" / "amount").exists()
        assert (splayed_dir / f"{i}" / "test" / "status").exists()

    loaded_table = Table.from_parted(f"{splayed_dir}/", "test")

    assert isinstance(loaded_table, Table)
    columns = loaded_table.columns()
    assert len(columns) == 4
    assert Symbol("Date") in columns  # this is default partitioning criteria
    assert Symbol("category") in columns
    assert Symbol("amount") in columns
    assert Symbol("status") in columns

    values = loaded_table.select("*").execute().values()
    assert len(values) == 4

    date_col, category_col, amount_col, status_col = values
    assert [s.value for s in category_col] == [
        "A",
        "B",
        "C",
        "D",
        "A",
        "B",
        "C",
        "D",
        "A",
        "B",
        "C",
        "D",
    ]
    assert [v.value for v in amount_col] == [
        100,
        200,
        150,
        250,
        100,
        200,
        150,
        250,
        100,
        200,
        150,
        250,
    ]
    assert [s.value for s in status_col] == [
        "active",
        "inactive",
        "active",
        "active",
        "active",
        "inactive",
        "active",
        "active",
        "active",
        "inactive",
        "active",
        "active",
    ]


@pytest.mark.xfail(reason="Temporarily - COW is called, destructive operations are allowed")
def test_splayed_table_destructive_operations_raise_error(tmp_path):
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        }
    )

    splayed_dir = tmp_path / "test_splayed_destructive"
    splayed_dir.mkdir()
    table.set_splayed(f"{splayed_dir}/")

    loaded_table = Table.from_splayed(f"{splayed_dir}/")
    assert loaded_table.is_parted is True

    with pytest.raises(PartedTableError, match="use .select\\(\\) first"):
        loaded_table.values()

    with pytest.raises(PartedTableError, match="use .select\\(\\) first"):
        loaded_table.update(age=100)

    with pytest.raises(PartedTableError, match="use .select\\(\\) first"):
        loaded_table.insert(id="003", name="charlie", age=41)

    with pytest.raises(PartedTableError, match="use .select\\(\\) first"):
        loaded_table.upsert(id="001", name="alice_updated", age=30, match_by_first=1)


@pytest.mark.xfail(reason="Temporarily - COW is called, destructive operations are allowed")
def test_parted_table_destructive_operations_raise_error(tmp_path):
    table = Table.from_dict(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        }
    )

    splayed_dir = tmp_path / "test_parted_destructive"
    splayed_dir.mkdir()

    table.set_splayed(f"{splayed_dir}/2024.01.01/test/", f"{splayed_dir}/sym")

    loaded_table = Table.from_parted(f"{splayed_dir}/", "test")
    assert loaded_table.is_parted is True

    with pytest.raises(PartedTableError, match="use .select\\(\\) first"):
        loaded_table.values()

    with pytest.raises(PartedTableError, match="use .select\\(\\) first"):
        loaded_table.update(age=100)

    with pytest.raises(PartedTableError, match="use .select\\(\\) first"):
        loaded_table.insert(id="003", name="charlie", age=41)

    with pytest.raises(PartedTableError, match="use .select\\(\\) first"):
        loaded_table.upsert(id="001", name="alice_updated", age=30, match_by_first=1)
