import numpy as np
import pytest

from rayforce import errors
from rayforce.types import Column, Dict, Table, Vector
from rayforce.types.scalars import B8, F64, I64, Date, Symbol, Time, Timestamp
from tests.helpers.assertions import (
    assert_column_values,
    assert_contains_columns,
    assert_table_shape,
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

    assert_column_values(table, "i64", [1, 2])
    assert [round(v.value, 6) for v in f64_col] == [1.5, 2.5]
    assert_column_values(table, "b8", [True, False])

    # Date column
    assert [d.value.isoformat() for d in date_col] == ["2001-01-02", "2001-01-03"]

    # Time column
    # TODO: CSV parser doesn't properly support Time type yet

    # Timestamp column - compare date/time portion, ignore timezone details
    ts_str = [ts.value.replace(tzinfo=None).isoformat(sep=" ") for ts in ts_col]
    assert ts_str == ["2001-01-02 09:00:00", "2001-01-03 10:00:00"]

    assert_column_values(table, "symbol", ["foo", "bar"])


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
    assert_table_shape(loaded_table, rows=3, cols=3)
    assert_column_values(loaded_table, "id", ["001", "002", "003"])
    assert_column_values(loaded_table, "name", ["alice", "bob", "charlie"])
    assert_column_values(loaded_table, "age", [29, 34, 41])


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

    assert csv_path.exists()

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

    result = loaded_table.select("*").execute()
    assert_table_shape(result, rows=4, cols=3)
    assert_column_values(result, "category", ["A", "B", "A", "B"])
    assert_column_values(result, "amount", [100, 200, 150, 250])
    assert_column_values(result, "status", ["active", "inactive", "active", "active"])


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

    result = loaded_table.select("*").execute()
    assert_contains_columns(result, ["date", "category", "amount", "status"])
    assert_table_shape(result, rows=12, cols=4)
    assert_column_values(result, "category", ["A", "B", "C", "D"] * 3)
    assert_column_values(result, "amount", [100, 200, 150, 250] * 3)
    assert_column_values(result, "status", ["active", "inactive", "active", "active"] * 3)


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
    assert_table_shape(result, rows=4, cols=3)
    assert_column_values(result, "id", ["001", "002", "003", "004"])
    assert_column_values(result, "name", ["alice", "bob", "charlie", "dana"])
    assert_column_values(result, "age", [29, 34, 41, 38])


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
    assert_table_shape(result, rows=3, cols=2)
    assert_column_values(result, "id", ["001", "002", "003"])
    assert_column_values(result, "value", [10, 20, 30])


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
    assert_table_shape(result, rows=2, cols=2)


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
    assert isinstance(name_col, Vector)
    assert len(name_col) == 4
    assert_column_values(table, "name", ["alice", "bob", "charlie", "dana"])
    assert_column_values(table, "age", [29, 34, 41, 38])
    assert_column_values(table, "salary", [100000, 120000, 90000, 85000])
    assert_column_values(table, "id", ["001", "002", "003", "004"])


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
    assert row_0.to_python() == {"id": "001", "name": "alice", "age": 29, "salary": 100000}

    assert isinstance(row_2, Dict)
    assert row_2.to_python() == {"id": "003", "name": "charlie", "age": 41, "salary": 90000}

    assert isinstance(row_3, Dict)
    assert row_3.to_python() == {"id": "004", "name": "dana", "age": 38, "salary": 85000}


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
    assert_table_shape(result, rows=2, cols=3)
    assert_column_values(result, "id", ["001", "002"])
    assert_column_values(result, "name", ["alice", "bob"])
    assert_column_values(result, "age", [29, 34])

    # Take first 3 rows
    result = table.take(3)
    assert_table_shape(result, rows=3, cols=3)
    assert_column_values(result, "id", ["001", "002", "003"])
    assert_column_values(result, "name", ["alice", "bob", "charlie"])
    assert_column_values(result, "age", [29, 34, 41])


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
    assert_table_shape(result, rows=2, cols=3)
    assert_column_values(result, "id", ["002", "003"])
    assert_column_values(result, "name", ["bob", "charlie"])
    assert_column_values(result, "age", [34, 41])

    # Take 3 rows starting from offset 0
    result = table.take(3, offset=0)
    assert_table_shape(result, rows=3, cols=3)
    assert_column_values(result, "id", ["001", "002", "003"])
    assert_column_values(result, "name", ["alice", "bob", "charlie"])
    assert_column_values(result, "age", [29, 34, 41])


@pytest.mark.parametrize("is_inplace", [True, False])
def test_shape(is_inplace, make_table):
    num_rows = 1000
    data = {
        "id": Vector(items=list(range(num_rows)), ray_type=I64),
        "value": Vector(items=[float(i) * 1.5 for i in range(num_rows)], ray_type=F64),
        "category": Vector(items=[f"cat_{i % 10}" for i in range(num_rows)], ray_type=Symbol),
    }

    if is_inplace:
        result = Table(data).shape()
    else:
        name, _ = make_table(data)
        result = Table(name).shape()

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
    assert_column_values(table, "name", ["alice", "bob", "charlie"])
    assert_column_values(table, "age", [29, 34, 41])


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


def test_getitem_expression_filter():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
        }
    )

    result = table[Column("age") > 35]
    assert isinstance(result, Table)
    assert len(result) == 2
    assert_column_values(result, "name", ["charlie", "dana"])
    assert_column_values(result, "age", [41, 38])


def test_getitem_expression_equals():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "dept": Vector(items=["eng", "sales", "eng"], ray_type=Symbol),
        }
    )

    result = table[Column("dept") == "eng"]
    assert len(result) == 2
    assert_column_values(result, "name", ["alice", "charlie"])


def test_getitem_expression_or():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
        }
    )

    result = table[(Column("age") < 30) | (Column("age") > 40)]
    assert len(result) == 2
    assert_column_values(result, "name", ["alice", "charlie"])


def test_getitem_combined_expression():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
            "dept": Vector(items=["eng", "sales", "eng", "sales"], ray_type=Symbol),
        }
    )

    result = table[(Column("age") > 30) & (Column("dept") == "eng")]
    assert isinstance(result, Table)
    assert len(result) == 1
    assert_column_values(result, "name", ["charlie"])


def test_getitem_expression_no_match():
    table = Table(
        {
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        }
    )

    result = table[Column("age") > 100]
    assert isinstance(result, Table)
    assert len(result) == 0


def test_getitem_expression_all_match():
    table = Table(
        {
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        }
    )

    result = table[Column("age") > 0]
    assert len(result) == 2
    assert_column_values(result, "name", ["alice", "bob"])


def test_getitem_int_row():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41], ray_type=I64),
        }
    )

    first = table[0]
    assert isinstance(first, Dict)
    assert first["name"] == "alice"
    assert first["age"] == 29

    middle = table[1]
    assert middle["name"] == "bob"

    last = table[-1]
    assert isinstance(last, Dict)
    assert last["name"] == "charlie"
    assert last["age"] == 41


def test_getitem_int_row_second_to_last():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
        }
    )

    assert table[-2]["name"] == "bob"


def test_getitem_slice_start_stop():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie", "dana", "eve"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38, 25], ray_type=I64),
        }
    )

    result = table[1:3]
    assert isinstance(result, Table)
    assert len(result) == 2
    assert_column_values(result, "name", ["bob", "charlie"])
    assert_column_values(result, "age", [34, 41])


def test_getitem_slice_head():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie", "dana", "eve"], ray_type=Symbol),
        }
    )

    result = table[:2]
    assert len(result) == 2
    assert_column_values(result, "name", ["alice", "bob"])

    result = table[:0]
    assert len(result) == 0


def test_getitem_slice_tail():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie", "dana", "eve"], ray_type=Symbol),
        }
    )

    result = table[-2:]
    assert len(result) == 2
    assert_column_values(result, "name", ["dana", "eve"])

    result = table[-1:]
    assert len(result) == 1
    assert_column_values(result, "name", ["eve"])


def test_getitem_slice_full():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
        }
    )

    result = table[:]
    assert len(result) == 3
    assert_column_values(result, "name", ["alice", "bob", "charlie"])


def test_getitem_slice_from_offset_to_end():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
        }
    )

    result = table[2:]
    assert len(result) == 2
    assert_column_values(result, "name", ["charlie", "dana"])


def test_getitem_slice_negative_stop():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie", "dana", "eve"], ray_type=Symbol),
        }
    )

    # table[1:-1] → middle three
    result = table[1:-1]
    assert len(result) == 3
    assert_column_values(result, "name", ["bob", "charlie", "dana"])


def test_getitem_slice_beyond_length():
    table = Table(
        {
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        }
    )

    # take pads when n > length, matching C-level TAKE semantics
    result = table[:100]
    assert len(result) >= 2


def test_getitem_slice_empty_range():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
        }
    )

    result = table[2:1]
    assert len(result) == 0


def test_getitem_slice_step_raises():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
        }
    )

    with pytest.raises(errors.RayforceIndexError, match="step"):
        table[::2]


def test_getitem_int_list():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie", "dana"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41, 38], ray_type=I64),
        }
    )

    result = table[[0, 2]]
    assert isinstance(result, Table)
    assert len(result) == 2
    assert_column_values(result, "name", ["alice", "charlie"])
    assert_column_values(result, "age", [29, 41])


def test_getitem_int_list_single():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
        }
    )

    result = table[[1]]
    assert isinstance(result, Table)
    assert len(result) == 1
    assert_column_values(result, "name", ["bob"])


def test_getitem_int_list_reversed_order():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
        }
    )

    result = table[[2, 0]]
    assert len(result) == 2
    assert_column_values(result, "name", ["charlie", "alice"])


def test_getitem_int_list_with_duplicates():
    table = Table(
        {
            "name": Vector(items=["alice", "bob", "charlie"], ray_type=Symbol),
        }
    )

    result = table[[0, 0, 2]]
    assert len(result) == 3
    assert_column_values(result, "name", ["alice", "alice", "charlie"])


def test_getitem_empty_list_raises():
    table = Table(
        {
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        }
    )

    with pytest.raises(errors.RayforceIndexError, match="empty"):
        table[[]]


def test_getitem_list_wrong_type_raises():
    table = Table(
        {
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        }
    )

    with pytest.raises(errors.RayforceTypeError, match="str or int"):
        table[[3.14]]


def test_getitem_invalid_type_raises():
    table = Table(
        {
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        }
    )

    with pytest.raises(errors.RayforceTypeError, match="Invalid index type"):
        table[3.14]


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
    assert_column_values(result, "id", ["001", "002"])
    assert_column_values(result, "name", ["alice", "bob"])


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
    assert_column_values(result, "id", ["004", "005"])
    assert_column_values(result, "name", ["dana", "eve"])


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
    assert_column_values(result, "full_name", ["alice", "bob", "charlie"])


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

    assert_column_values(result, "age", [29.0, 34.0, 41.0])


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
    assert_column_values(result, "price", [10, 20, 30])


def test_cast_unknown_column_raises():
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
        }
    )

    with pytest.raises(errors.RayforceConversionError, match="Column not found"):
        table.cast("unknown", F64)


# ---------------------------------------------------------------------------
# concat edge cases
# ---------------------------------------------------------------------------


def test_concat_with_mismatched_column_names():
    """Concatenating tables with different column names raises a value error.

    v1 raised ``RayforceValueError`` with a "column mismatch" message; v2 uses
    packed error codes and the readable message is out-of-band, so the test
    asserts on the error class/code rather than the text.
    """
    table1 = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
        }
    )
    table2 = Table(
        {
            "id": Vector(items=["003"], ray_type=Symbol),
            "different_col": Vector(items=["charlie"], ray_type=Symbol),
        }
    )

    with pytest.raises(errors.RayforceValueError):
        table1.concat(table2)


def test_concat_with_mismatched_column_types():
    """Concatenating tables with same names but different types raises RayforceTypeError."""
    table1 = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "value": Vector(items=[1, 2], ray_type=I64),
        }
    )
    table2 = Table(
        {
            "id": Vector(items=["003"], ray_type=Symbol),
            "value": Vector(items=[3.0], ray_type=F64),
        }
    )

    with pytest.raises(errors.RayforceTypeError):
        table1.concat(table2)


# ---------------------------------------------------------------------------
# at_row / at_column edge cases
# ---------------------------------------------------------------------------


def test_at_column_with_nonexistent_column():
    """at_column with a column name that does not exist raises a domain error.

    v1 returned ``Null`` for a missing column; v2 treats a missing column as a
    domain error from ``(at t 'name)``. The test asserts on the error class/code
    rather than the (currently empty) v2 message text.
    """
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        }
    )

    with pytest.raises(errors.RayforceDomainError):
        table.at_column("nonexistent")


# ---------------------------------------------------------------------------
# take edge cases
# ---------------------------------------------------------------------------


def test_take_with_offset_beyond_total_rows():
    """take() with offset larger than total rows returns an empty table."""
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41], ray_type=I64),
        }
    )

    result = table.take(2, offset=10)

    assert_table_shape(result, rows=0, cols=2)


# ---------------------------------------------------------------------------
# rename edge cases
# ---------------------------------------------------------------------------


def test_rename_creating_duplicate_column_names():
    """Renaming a column to a name that already exists raises rather than silently merging."""
    table = Table(
        {
            "id": Vector(items=["001", "002"], ray_type=Symbol),
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        }
    )

    with pytest.raises(errors.RayforceConversionError, match="duplicate"):
        table.rename({"id": "name"})


# ---------------------------------------------------------------------------
# cast edge cases
# ---------------------------------------------------------------------------


def test_cast_with_incompatible_types():
    """Casting Symbol to I64 raises RayforceTypeError."""
    table = Table(
        {
            "name": Vector(items=["alice", "bob"], ray_type=Symbol),
            "age": Vector(items=[29, 34], ray_type=I64),
        }
    )

    with pytest.raises(errors.RayforceTypeError):
        table.cast("name", I64)


# ---------------------------------------------------------------------------
# describe edge cases
# ---------------------------------------------------------------------------


def test_describe_on_empty_table():
    """describe() on a table with zero rows returns an empty stats dict."""
    table = Table(
        {
            "age": Vector(items=[], ray_type=I64),
            "salary": Vector(items=[], ray_type=F64),
        }
    )

    stats = table.describe()
    assert stats == {}


# ---------------------------------------------------------------------------
# head / tail edge cases
# ---------------------------------------------------------------------------


def test_head_with_n_greater_than_total_rows():
    """head(n) with n > total rows wraps cyclically, returning n rows."""
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41], ray_type=I64),
        }
    )

    result = table.head(5)
    assert len(result) == 5
    # First 3 rows are the original; rows 4-5 wrap to the beginning
    assert_column_values(result, "id", ["001", "002", "003", "001", "002"])


def test_tail_with_n_greater_than_total_rows():
    """tail(n) with n > total rows wraps cyclically, returning n rows."""
    table = Table(
        {
            "id": Vector(items=["001", "002", "003"], ray_type=Symbol),
            "age": Vector(items=[29, 34, 41], ray_type=I64),
        }
    )

    result = table.tail(5)
    assert len(result) == 5
    # Tail wraps cyclically from the end
    assert_column_values(result, "id", ["002", "003", "001", "002", "003"])


# --- Table.to_dict() ---


class TestTableToDict:
    def test_basic(self):
        table = Table(
            {
                "id": Vector([1, 2, 3], ray_type=I64),
                "score": Vector([95.5, 87.3, 92.1], ray_type=F64),
            }
        )
        d = table.to_dict()
        assert d == {"id": [1, 2, 3], "score": [95.5, 87.3, 92.1]}

    def test_with_symbols(self):
        table = Table(
            {
                "name": Vector(["alice", "bob"], ray_type=Symbol),
                "age": Vector([25, 30], ray_type=I64),
            }
        )
        d = table.to_dict()
        assert d == {"name": ["alice", "bob"], "age": [25, 30]}

    def test_single_column(self):
        table = Table({"x": Vector([10, 20, 30], ray_type=I64)})
        d = table.to_dict()
        assert d == {"x": [10, 20, 30]}

    def test_single_row(self):
        table = Table(
            {
                "a": Vector([1], ray_type=I64),
                "b": Vector([2.0], ray_type=F64),
            }
        )
        d = table.to_dict()
        assert d == {"a": [1], "b": [2.0]}


# --- Table.to_numpy() ---


class TestTableToNumpy:
    def test_numeric_columns(self):
        table = Table(
            {
                "a": Vector([1, 2, 3], ray_type=I64),
                "b": Vector([4.0, 5.0, 6.0], ray_type=F64),
            }
        )
        arr = table.to_numpy()
        assert arr.shape == (3, 2)
        assert arr.dtype == np.float64
        np.testing.assert_array_equal(arr[:, 0], [1, 2, 3])
        np.testing.assert_array_equal(arr[:, 1], [4.0, 5.0, 6.0])

    def test_single_column(self):
        table = Table({"x": Vector([10, 20, 30], ray_type=I64)})
        arr = table.to_numpy()
        assert arr.shape == (3, 1)
        np.testing.assert_array_equal(arr[:, 0], [10, 20, 30])

    def test_single_row(self):
        table = Table(
            {
                "a": Vector([1], ray_type=I64),
                "b": Vector([2], ray_type=I64),
            }
        )
        arr = table.to_numpy()
        assert arr.shape == (1, 2)

    def test_mixed_types_coerced(self):
        table = Table(
            {
                "name": Vector(["alice", "bob"], ray_type=Symbol),
                "age": Vector([25, 30], ray_type=I64),
            }
        )
        arr = table.to_numpy()
        assert arr.shape == (2, 2)
        # Mixed types coerce to string dtype
        assert arr[0, 0] == "alice"
        assert arr[0, 1] == "25"

    def test_with_timestamp_column(self):
        from datetime import datetime

        table = Table.from_dict(
            {
                "id": Vector([1, 2, 3], ray_type=I64),
                "name": Vector(["Alice", "Bob", "Carol"], ray_type=Symbol),
            }
        )
        birthdays = Vector(
            [datetime(2001, 1, 1), datetime(2002, 2, 2), datetime(2003, 3, 3)],
            ray_type=Timestamp,
        )
        table = table.select("*", birthday=birthdays).execute()
        arr = table.to_numpy()
        assert arr.shape == (3, 3)
        assert arr.dtype == object
        assert arr[0, 2] == datetime(2001, 1, 1)
        assert arr[2, 2] == datetime(2003, 3, 3)
        assert isinstance(arr[0, 2], datetime)

    def test_with_all_temporal_columns(self):
        from datetime import date, datetime, time, timedelta

        table = Table.from_dict(
            {
                "id": Vector([1, 2], ray_type=I64),
                "dt": Vector([date(2001, 1, 1), date(2002, 2, 2)], ray_type=Date),
                "tm": Vector([time(9, 0), time(10, 30)], ray_type=Time),
                "ts": Vector(
                    [datetime(2001, 1, 1, 9, 0), datetime(2002, 2, 2, 10, 30)],
                    ray_type=Timestamp,
                ),
            }
        )
        arr = table.to_numpy()
        assert arr.shape == (2, 4)
        assert arr.dtype == object

        # Date → datetime (datetime64[D].astype(object) produces datetime)
        assert arr[0, 1] == datetime(2001, 1, 1)

        # Time → timedelta
        assert isinstance(arr[0, 2], timedelta)
        assert arr[0, 2] == timedelta(hours=9)

        # Timestamp → datetime
        assert isinstance(arr[0, 3], datetime)
        assert arr[0, 3] == datetime(2001, 1, 1, 9, 0)

    def test_all_same_int_type(self):
        table = Table(
            {
                "x": Vector([1, 2], ray_type=I64),
                "y": Vector([3, 4], ray_type=I64),
                "z": Vector([5, 6], ray_type=I64),
            }
        )
        arr = table.to_numpy()
        assert arr.dtype == np.int64
        assert arr.shape == (2, 3)
        np.testing.assert_array_equal(arr, [[1, 3, 5], [2, 4, 6]])


class TestTableFromDict:
    def test_from_numpy_arrays(self):
        table = Table.from_dict(
            {
                "id": np.array([1, 2, 3], dtype=np.int64),
                "score": np.array([95.5, 87.3, 92.1], dtype=np.float64),
            }
        )
        assert_contains_columns(table, ["id", "score"])
        assert_column_values(table, "id", [1, 2, 3])

    def test_from_python_lists(self):
        table = Table.from_dict(
            {
                "name": ["alice", "bob", "charlie"],
                "age": [25, 30, 35],
            }
        )
        assert_contains_columns(table, ["name", "age"])
        assert_column_values(table, "name", ["alice", "bob", "charlie"])

    def test_from_vectors(self):
        table = Table.from_dict(
            {
                "x": Vector([10, 20, 30], ray_type=I64),
                "y": Vector([1.0, 2.0, 3.0], ray_type=F64),
            }
        )
        assert_contains_columns(table, ["x", "y"])
        assert_column_values(table, "x", [10, 20, 30])

    def test_mixed_sources(self):
        table = Table.from_dict(
            {
                "np_col": np.array([1, 2, 3], dtype=np.int64),
                "list_col": [10, 20, 30],
                "vec_col": Vector([100, 200, 300], ray_type=I64),
            }
        )
        assert_contains_columns(table, ["np_col", "list_col", "vec_col"])
        assert_column_values(table, "np_col", [1, 2, 3])
        assert_column_values(table, "list_col", [10, 20, 30])
        assert_column_values(table, "vec_col", [100, 200, 300])

    def test_from_numpy_string_array(self):
        table = Table.from_dict(
            {
                "name": np.array(["alice", "bob", "charlie"]),
                "age": np.array([25, 30, 35], dtype=np.int64),
            }
        )
        assert_contains_columns(table, ["name", "age"])
        assert_column_values(table, "name", ["alice", "bob", "charlie"])
        assert_column_values(table, "age", [25, 30, 35])

    def test_roundtrip_to_dict(self):
        original = {
            "a": np.array([1, 2, 3], dtype=np.int64),
            "b": np.array([4.0, 5.0, 6.0], dtype=np.float64),
        }
        table = Table.from_dict(original)
        result = table.to_dict()
        assert result["a"] == [1, 2, 3]
        np.testing.assert_array_almost_equal(result["b"], [4.0, 5.0, 6.0])

    def test_roundtrip_to_numpy(self):
        original = {
            "a": np.array([1, 2, 3], dtype=np.int64),
            "b": np.array([4, 5, 6], dtype=np.int64),
        }
        table = Table.from_dict(original)
        arr = table.to_numpy()
        assert arr.shape == (3, 2)
        np.testing.assert_array_equal(arr[:, 0], [1, 2, 3])
        np.testing.assert_array_equal(arr[:, 1], [4, 5, 6])

    def test_single_column(self):
        table = Table.from_dict({"x": np.array([10, 20], dtype=np.int64)})
        assert_contains_columns(table, ["x"])
        assert_column_values(table, "x", [10, 20])

    def test_large_numpy(self):
        n = 1_000_000
        table = Table.from_dict(
            {
                "a": np.arange(n, dtype=np.int64),
                "b": np.arange(n, dtype=np.float64),
            }
        )
        assert len(table) == n
        d = table.to_dict()
        assert d["a"][0] == 0
        assert d["a"][-1] == n - 1


class TestTableConversionLarge:
    """Performance tests with 20M+ row tables."""

    N = 20_000_000

    def test_to_dict_20m(self):
        table = Table.from_dict(
            {
                "a": np.arange(self.N, dtype=np.int64),
                "b": np.arange(self.N, dtype=np.float64),
            }
        )
        d = table.to_dict()
        assert len(d["a"]) == self.N
        assert len(d["b"]) == self.N
        assert d["a"][0] == 0
        assert d["a"][-1] == self.N - 1
        assert d["b"][0] == 0.0
        assert d["b"][-1] == float(self.N - 1)

    def test_to_numpy_20m(self):
        table = Table.from_dict(
            {
                "a": np.arange(self.N, dtype=np.int64),
                "b": np.arange(self.N, dtype=np.float64),
            }
        )
        arr = table.to_numpy()
        assert arr.shape == (self.N, 2)
        assert arr[0, 0] == 0
        assert arr[-1, 0] == self.N - 1
        assert arr[0, 1] == 0.0
        assert arr[-1, 1] == float(self.N - 1)
