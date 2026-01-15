import pytest

from rayforce import errors
from rayforce.types import Dict, Table, Vector
from rayforce.types.scalars import B8, F64, I64, Date, Symbol, Time, Timestamp


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


def test_set_csv(tmp_path):
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41], ray_type=I64),
        }
    )

    csv_path = tmp_path / "test_table.csv"
    table.set_csv(str(csv_path))
    assert csv_path.exists()

    loaded_table = Table.from_csv([Symbol, Symbol, I64], str(csv_path))

    assert isinstance(loaded_table, Table)
    columns = loaded_table.columns()
    assert len(columns) == 3
    assert Symbol("id") in columns
    assert Symbol("name") in columns
    assert Symbol("age") in columns

    values = loaded_table.values()
    assert len(values) == 3

    column_dict = {col.value: idx for idx, col in enumerate(columns)}
    id_col = values[column_dict["id"]]
    name_col = values[column_dict["name"]]
    age_col = values[column_dict["age"]]

    assert [s.value for s in id_col] == ["001", "002", "003"]
    assert [s.value for s in name_col] == ["alice", "bob", "charlie"]
    assert [v.value for v in age_col] == [29, 34, 41]


def test_set_csv_with_custom_separator(tmp_path):
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        }
    )

    csv_path = tmp_path / "test_table_sep.csv"
    table.set_csv(str(csv_path), separator=";")

    # Verify file was created
    assert csv_path.exists()

    # Verify the file uses semicolon separator by reading it
    csv_content = csv_path.read_text()
    lines = csv_content.strip().split("\n")
    assert len(lines) >= 2  # Header + at least one data row
    assert ";" in lines[0]  # Header should contain semicolon


def test_set_splayed_and_from_splayed(tmp_path):
    table = Table(
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
    table = Table(
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
    table = Table(
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

    with pytest.raises(errors.RayforcePartedTableError, match="use .select\\(\\) first"):
        loaded_table.values()

    with pytest.raises(errors.RayforcePartedTableError, match="use .select\\(\\) first"):
        loaded_table.update(age=100)

    with pytest.raises(errors.RayforcePartedTableError, match="use .select\\(\\) first"):
        loaded_table.insert(id="003", name="charlie", age=41)

    with pytest.raises(errors.RayforcePartedTableError, match="use .select\\(\\) first"):
        loaded_table.upsert(id="001", name="alice_updated", age=30, key_columns=1)


@pytest.mark.xfail(reason="Temporarily - COW is called, destructive operations are allowed")
def test_parted_table_destructive_operations_raise_error(tmp_path):
    table = Table(
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

    with pytest.raises(errors.RayforcePartedTableError, match="use .select\\(\\) first"):
        loaded_table.values()

    with pytest.raises(errors.RayforcePartedTableError, match="use .select\\(\\) first"):
        loaded_table.update(age=100)

    with pytest.raises(errors.RayforcePartedTableError, match="use .select\\(\\) first"):
        loaded_table.insert(id="003", name="charlie", age=41)

    with pytest.raises(errors.RayforcePartedTableError, match="use .select\\(\\) first"):
        loaded_table.upsert(id="001", name="alice_updated", age=30, key_columns=1)


def test_concat_two_tables():
    table1 = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        }
    )

    table2 = Table(
        {
            "id": Vector(items=["003", "004"], ray_type=Symbol),
            "name": Vector(items=["charlie", "dana"], ray_type=Symbol),
            "age": Vector(items=[41, 38], ray_type=I64),
        }
    )

    result = table1.concat(table2)

    assert isinstance(result, Table)
    columns = result.columns()
    assert len(columns) == 3
    assert Symbol("id") in columns
    assert Symbol("name") in columns
    assert Symbol("age") in columns

    values = result.values()
    assert len(values) == 3
    assert len(values[0]) == 4  # Should have 4 rows total

    id_col, name_col, age_col = values
    assert [s.value for s in id_col] == ["001", "002", "003", "004"]
    assert [s.value for s in name_col] == ["alice", "bob", "charlie", "dana"]
    assert [v.value for v in age_col] == [29, 34, 41, 38]


def test_concat_multiple_tables():
    table1 = Table(
        {
            "id": Vector(items=["001"], ray_type=Symbol),
            "value": Vector(items=[10], ray_type=I64),
        }
    )

    table2 = Table(
        {
            "id": Vector(items=["002"], ray_type=Symbol),
            "value": Vector(items=[20], ray_type=I64),
        }
    )

    table3 = Table(
        {
            "id": Vector(items=["003"], ray_type=Symbol),
            "value": Vector(items=[30], ray_type=I64),
        }
    )

    result = table1.concat(table2, table3)

    assert isinstance(result, Table)
    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 3  # Should have 3 rows total

    id_col, value_col = values
    assert [s.value for s in id_col] == ["001", "002", "003"]
    assert [v.value for v in value_col] == [10, 20, 30]


def test_concat_empty_others():
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        }
    )

    result = table.concat()

    assert isinstance(result, Table)
    assert result is table  # Should return the same table when no others provided
    values = result.values()
    assert len(values) == 2
    assert len(values[0]) == 2


def test_at_column():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
            "salary": Vector(items=[100000, 120000, 90000, 85000], ray_type=I64),
        }
    )

    name_col = table.at_column("name")
    age_col = table.at_column("age")
    salary_col = table.at_column("salary")
    id_col = table.at_column("id")

    assert isinstance(name_col, Vector)
    assert len(name_col) == 4
    assert [item.value for item in name_col] == ["alice", "bob", "charlie", "dana"]

    assert isinstance(age_col, Vector)
    assert len(age_col) == 4
    assert [item.value for item in age_col] == [29, 34, 41, 38]

    assert isinstance(salary_col, Vector)
    assert len(salary_col) == 4
    assert [item.value for item in salary_col] == [100000, 120000, 90000, 85000]

    assert isinstance(id_col, Vector)
    assert len(id_col) == 4
    assert [item.value for item in id_col] == ["001", "002", "003", "004"]


def test_at_row():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
            "salary": Vector(items=[100000, 120000, 90000, 85000], ray_type=I64),
        }
    )

    row_0 = table.at_row(0)
    row_2 = table.at_row(2)
    row_3 = table.at_row(3)

    assert isinstance(row_0, Dict)
    assert row_0.to_python() == {
        "id": "001",
        "name": "alice",
        "age": 29,
        "salary": 100000,
    }

    assert isinstance(row_2, Dict)
    assert row_2.to_python() == {
        "id": "003",
        "name": "charlie",
        "age": 41,
        "salary": 90000,
    }

    assert isinstance(row_3, Dict)
    assert row_3.to_python() == {
        "id": "004",
        "name": "dana",
        "age": 38,
        "salary": 85000,
    }


def test_take_rows():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004", "005"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana", "eve"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38, 25], ray_type=I64),
        }
    )

    # Take first 2 rows
    result = table.take(2)
    assert isinstance(result, Table)
    values = result.values()
    assert len(values) == 3
    assert len(values[0]) == 2

    id_col, name_col, age_col = values
    assert [s.value for s in id_col] == ["001", "002"]
    assert [s.value for s in name_col] == ["alice", "bob"]
    assert [v.value for v in age_col] == [29, 34]

    # Take first 3 rows
    result = table.take(3)
    values = result.values()
    assert len(values[0]) == 3

    id_col, name_col, age_col = values
    assert [s.value for s in id_col] == ["001", "002", "003"]
    assert [s.value for s in name_col] == ["alice", "bob", "charlie"]
    assert [v.value for v in age_col] == [29, 34, 41]


def test_take_with_offset():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004", "005"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana", "eve"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38, 25], ray_type=I64),
        }
    )

    # Take 2 rows starting from offset 1
    result = table.take(2, offset=1)
    assert isinstance(result, Table)
    values = result.values()
    assert len(values) == 3
    assert len(values[0]) == 2

    id_col, name_col, age_col = values
    assert [s.value for s in id_col] == ["002", "003"]
    assert [s.value for s in name_col] == ["bob", "charlie"]
    assert [v.value for v in age_col] == [34, 41]

    # Take 3 rows starting from offset 0
    result = table.take(3, offset=0)
    values = result.values()
    assert len(values[0]) == 3

    id_col, name_col, age_col = values
    assert [s.value for s in id_col] == ["001", "002", "003"]
    assert [s.value for s in name_col] == ["alice", "bob", "charlie"]
    assert [v.value for v in age_col] == [29, 34, 41]


@pytest.mark.parametrize("is_inplace", [True, False])
def test_shape(is_inplace):
    num_rows = 1000
    table = Table(
        {
            "id": Vector(items=list(range(num_rows)), ray_type=I64),
            "value": Vector(items=[float(i) * 1.5 for i in range(num_rows)], ray_type=F64),
            "category": Vector(items=[f"cat_{i % 10}" for i in range(num_rows)], ray_type=Symbol),
        },
    )

    if is_inplace:
        result = table.shape()
    else:
        table.save("test_shape_large")
        result = Table("test_shape_large").shape()

    assert result == (num_rows, 3)


def test_len():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004", "005"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana", "eve"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38, 25], ray_type=I64),
        }
    )

    assert len(table) == 5


def test_getitem_single_column():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41], ray_type=I64),
        }
    )

    name_col = table["name"]
    assert len(name_col) == 3
    assert [s.value for s in name_col] == ["alice", "bob", "charlie"]

    age_col = table["age"]
    assert [v.value for v in age_col] == [29, 34, 41]


def test_getitem_multiple_columns():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41], ray_type=I64),
        }
    )

    result = table[["id", "name"]]
    assert isinstance(result, Table)
    columns = result.columns()
    assert len(columns) == 2
    assert Symbol("id") in columns
    assert Symbol("name") in columns
    assert Symbol("age") not in columns


def test_head():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004", "005"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana", "eve"], ray_type=Symbol),
        }
    )

    # Default head (5 rows)
    result = table.head()
    assert len(result) == 5

    # Head with n=2
    result = table.head(2)
    assert len(result) == 2
    values = result.values()
    assert [s.value for s in values[0]] == ["001", "002"]
    assert [s.value for s in values[1]] == ["alice", "bob"]


def test_tail():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004", "005"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie", "dana", "eve"], ray_type=Symbol),
        }
    )

    # Tail with n=2
    result = table.tail(2)
    assert len(result) == 2
    values = result.values()
    assert [s.value for s in values[0]] == ["004", "005"]
    assert [s.value for s in values[1]] == ["dana", "eve"]


def test_describe():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003", "004"], ray_type=Symbol),
            "age": Vector(items=[20, 30, 40, 50], ray_type=I64),
            "salary": Vector(items=[50000.0, 60000.0, 70000.0, 80000.0], ray_type=F64),
        }
    )

    stats = table.describe()

    # Symbol column should be skipped
    assert "id" not in stats

    # Numeric columns should have stats
    assert "age" in stats
    assert stats["age"]["count"] == 4
    assert stats["age"]["mean"] == 35.0
    assert stats["age"]["min"] == 20
    assert stats["age"]["max"] == 50

    assert "salary" in stats
    assert stats["salary"]["count"] == 4
    assert stats["salary"]["mean"] == 65000.0
    assert stats["salary"]["min"] == 50000.0
    assert stats["salary"]["max"] == 80000.0


def test_dtypes():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41], ray_type=I64),
            "salary": Vector(items=[50000.0, 60000.0, 70000.0], ray_type=F64),
        }
    )

    dtypes = table.dtypes
    assert dtypes["id"] == "SYMBOL"
    assert dtypes["age"] == "I64"
    assert dtypes["salary"] == "F64"


def test_drop_single_column():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41], ray_type=I64),
        }
    )

    result = table.drop("age")
    assert isinstance(result, Table)
    columns = result.columns()
    assert len(columns) == 2
    assert Symbol("id") in columns
    assert Symbol("name") in columns
    assert Symbol("age") not in columns


def test_drop_multiple_columns():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41], ray_type=I64),
            "salary": Vector(items=[50000, 60000, 70000], ray_type=I64),
        }
    )

    result = table.drop("age", "salary")
    assert isinstance(result, Table)
    columns = result.columns()
    assert len(columns) == 2
    assert Symbol("id") in columns
    assert Symbol("name") in columns


def test_drop_unknown_column_raises():
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        }
    )

    with pytest.raises(errors.RayforceConversionError, match="Columns not found"):
        table.drop("unknown_column")


def test_rename_single_column():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41], ray_type=I64),
        }
    )

    result = table.rename({"name": "full_name"})
    assert isinstance(result, Table)
    columns = result.columns()
    assert Symbol("full_name") in columns
    assert Symbol("name") not in columns
    assert Symbol("id") in columns
    assert Symbol("age") in columns

    # Verify data is preserved
    full_name_col = result["full_name"]
    assert [s.value for s in full_name_col] == ["alice", "bob", "charlie"]


def test_rename_multiple_columns():
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        }
    )

    result = table.rename({"id": "user_id", "name": "full_name"})
    columns = result.columns()
    assert Symbol("user_id") in columns
    assert Symbol("full_name") in columns
    assert Symbol("id") not in columns
    assert Symbol("name") not in columns


def test_rename_unknown_column_raises():
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
        }
    )

    with pytest.raises(errors.RayforceConversionError, match="Columns not found"):
        table.rename({"unknown": "new_name"})


def test_cast_i64_to_f64():
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41], ray_type=I64),
        }
    )

    assert table.dtypes["age"] == "I64"

    result = table.cast("age", F64)
    assert result.dtypes["age"] == "F64"

    # Verify values are preserved
    age_col = result["age"]
    assert [v.value for v in age_col] == [29.0, 34.0, 41.0]


def test_cast_f64_to_i64():
    table = Table(
        {
            "price": Vector(items=[10.5, 20.7, 30.9], ray_type=F64),
        }
    )

    assert table.dtypes["price"] == "F64"

    result = table.cast("price", I64)
    assert result.dtypes["price"] == "I64"

    # Values are truncated when cast to int
    price_col = result["price"]
    assert [v.value for v in price_col] == [10, 20, 30]


def test_cast_unknown_column_raises():
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
        }
    )

    with pytest.raises(errors.RayforceConversionError, match="Column not found"):
        table.cast("unknown", F64)
