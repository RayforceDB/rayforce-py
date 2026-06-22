import datetime as dt

import pytest

from rayforce.plugins.pyarrow import from_arrow
from rayforce.types import B8, F64, I16, I32, I64, U8, Date, String, Symbol, Time, Timestamp
from rayforce.types.null import Null
from tests.helpers.assertions import (
    assert_column_values,
    assert_contains_columns,
    assert_table_shape,
)

pytestmark = pytest.mark.plugin


@pytest.fixture
def pyarrow():
    try:
        import pyarrow as pa

        return pa
    except ImportError:
        pytest.skip("pyarrow is not installed")


def test_from_arrow_basic_types(pyarrow):
    table = pyarrow.table(
        {
            "bool_col": pyarrow.array([True, False, True], pyarrow.bool_()),
            "i8_col": pyarrow.array([1, 2, 3], pyarrow.int8()),
            "i16_col": pyarrow.array([100, 200, 300], pyarrow.int16()),
            "i32_col": pyarrow.array([1000, 2000, 3000], pyarrow.int32()),
            "i64_col": pyarrow.array([10000, 20000, 30000], pyarrow.int64()),
            "f32_col": pyarrow.array([1.5, 2.5, 3.5], pyarrow.float32()),
            "f64_col": pyarrow.array([10.5, 20.5, 30.5], pyarrow.float64()),
            "str_col": pyarrow.array(["a", "b", "c"], pyarrow.string()),
        }
    )

    result = from_arrow(table)

    assert_table_shape(result, rows=3, cols=8)
    assert_contains_columns(
        result,
        ["bool_col", "i8_col", "i16_col", "i32_col", "i64_col", "f32_col", "f64_col", "str_col"],
    )


def test_from_arrow_boolean_type(pyarrow):
    table = pyarrow.table({"bool_col": pyarrow.array([True, False, True], pyarrow.bool_())})
    result = from_arrow(table)

    values = result.values()
    assert all(isinstance(v, B8) for v in values[0])
    assert_column_values(result, "bool_col", [True, False, True])


def test_from_arrow_integer_types(pyarrow):
    table = pyarrow.table(
        {
            "i8": pyarrow.array([1, 2, 3], pyarrow.int8()),
            "i16": pyarrow.array([100, 200, 300], pyarrow.int16()),
            "i32": pyarrow.array([1000, 2000, 3000], pyarrow.int32()),
            "i64": pyarrow.array([10000, 20000, 30000], pyarrow.int64()),
        }
    )

    result = from_arrow(table)
    values = result.values()

    # Type inference checks: i8 -> I16, i16 -> I16, i32 -> I32, i64 -> I64
    assert all(isinstance(v, I16) for v in values[0])  # i8 -> I16
    assert all(isinstance(v, I16) for v in values[1])  # i16 -> I16
    assert all(isinstance(v, I32) for v in values[2])  # i32 -> I32
    assert all(isinstance(v, I64) for v in values[3])  # i64 -> I64

    assert_column_values(result, "i8", [1, 2, 3])
    assert_column_values(result, "i16", [100, 200, 300])
    assert_column_values(result, "i32", [1000, 2000, 3000])
    assert_column_values(result, "i64", [10000, 20000, 30000])


def test_from_arrow_uint8_type(pyarrow):
    table = pyarrow.table({"u8": pyarrow.array([0, 1, 200, 255], pyarrow.uint8())})

    result = from_arrow(table)
    values = result.values()

    assert all(isinstance(v, U8) for v in values[0])
    assert_column_values(result, "u8", [0, 1, 200, 255])


def test_from_arrow_float_types(pyarrow):
    table = pyarrow.table(
        {
            "f32": pyarrow.array([1.5, 2.5, 3.5], pyarrow.float32()),
            "f64": pyarrow.array([10.5, 20.5, 30.5], pyarrow.float64()),
        }
    )

    result = from_arrow(table)
    values = result.values()

    for vector in values:
        assert all(isinstance(v, F64) for v in vector)

    assert_column_values(result, "f32", [1.5, 2.5, 3.5])
    assert_column_values(result, "f64", [10.5, 20.5, 30.5])


def test_from_arrow_string_types(pyarrow):
    table = pyarrow.table(
        {
            "str_col": pyarrow.array(["a", "b", "c"], pyarrow.string()),
            "large_str_col": pyarrow.array(["x", "y", "z"], pyarrow.large_string()),
        }
    )

    result = from_arrow(table)
    values = result.values()

    for vector in values:
        assert all(isinstance(v, String) for v in vector)

    assert_column_values(result, "str_col", ["a", "b", "c"])
    assert_column_values(result, "large_str_col", ["x", "y", "z"])


def test_from_arrow_strings_as_symbols(pyarrow):
    table = pyarrow.table(
        {
            "str_col": pyarrow.array(["a", "b", "c"], pyarrow.string()),
            "large_str_col": pyarrow.array(["x", "y", "z"], pyarrow.large_string()),
        }
    )

    result = from_arrow(table, strings_as_symbols=True)
    values = result.values()

    for vector in values:
        assert all(isinstance(v, Symbol) for v in vector)

    assert_column_values(result, "str_col", ["a", "b", "c"])
    assert_column_values(result, "large_str_col", ["x", "y", "z"])


def test_from_arrow_strings_as_symbols_leaves_other_types(pyarrow):
    table = pyarrow.table(
        {
            "id": pyarrow.array([1, 2, 3], pyarrow.int64()),
            "name": pyarrow.array(["a", "b", "c"], pyarrow.string()),
        }
    )

    result = from_arrow(table, strings_as_symbols=True)
    values = result.values()

    assert all(isinstance(v, I64) for v in values[0])  # id stays I64
    assert all(isinstance(v, Symbol) for v in values[1])  # name becomes Symbol


def test_from_arrow_datetime_types(pyarrow):
    dates = [dt.date(2023, 1, 1), dt.date(2023, 1, 2), dt.date(2023, 1, 3)]
    datetimes = [
        dt.datetime(2023, 1, 1, 12, 0, 0, tzinfo=dt.UTC),
        dt.datetime(2023, 1, 2, 12, 0, 0, tzinfo=dt.UTC),
        dt.datetime(2023, 1, 3, 12, 0, 0, tzinfo=dt.UTC),
    ]

    table = pyarrow.table(
        {
            "date_col": pyarrow.array(dates, pyarrow.date32()),
            "datetime_col": pyarrow.array(datetimes, pyarrow.timestamp("us", tz="UTC")),
        }
    )

    result = from_arrow(table)
    values = result.values()

    # Type inference checks
    assert all(isinstance(v, Date) for v in values[0] if v is not None)
    assert all(isinstance(v, Timestamp) for v in values[1] if v is not None)

    # Values must round-trip correctly (not just shape) — the buffer fast path is
    # bypassed for temporal columns precisely to keep these exact.
    assert_column_values(result, "date_col", dates)
    assert [v.to_python() for v in values[1]] == datetimes
    assert_table_shape(result, rows=3, cols=2)


def test_from_arrow_time_type(pyarrow):
    times = [dt.time(9, 0, 0), dt.time(17, 30, 0)]
    table = pyarrow.table({"time_col": pyarrow.array(times, pyarrow.time32("ms"))})

    result = from_arrow(table)
    values = result.values()

    assert all(isinstance(v, Time) for v in values[0] if v is not None)
    assert [v.to_python() for v in values[0]] == times


def test_from_arrow_with_nulls(pyarrow):
    table = pyarrow.table(
        {
            "int_col": pyarrow.array([1, None, 3], pyarrow.int64()),
            "float_col": pyarrow.array([1.5, None, 3.5], pyarrow.float64()),
            "string_col": pyarrow.array(["a", None, "c"], pyarrow.string()),
            "bool_col": pyarrow.array([True, None, False], pyarrow.bool_()),
        }
    )

    result = from_arrow(table)
    values = result.values()

    # Null handling for int column
    assert values[0][0].value == 1
    assert values[0][1] == Null
    assert values[0][2].value == 3

    # Null handling for float column
    assert values[1][0].value == 1.5
    assert values[1][1] == Null
    assert values[1][2].value == 3.5


def test_from_arrow_empty_table_raises(pyarrow):
    table = pyarrow.table({"col": pyarrow.array([], pyarrow.int64())})

    with pytest.raises(ValueError, match="Cannot convert empty Table"):
        from_arrow(table)


def test_from_arrow_wrong_type_raises():
    with pytest.raises(TypeError, match="Expected pyarrow.Table"):
        from_arrow("not a table")


def test_from_arrow_missing_dependency(monkeypatch):
    import sys

    from rayforce.plugins import pyarrow as pyarrow_module

    original_pyarrow = sys.modules.get("pyarrow")
    if "pyarrow" in sys.modules:
        del sys.modules["pyarrow"]

    original_import = __import__

    def mock_import(name, *args, **kwargs):
        if name == "pyarrow":
            raise ImportError("No module named 'pyarrow'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", mock_import)

    import importlib

    importlib.reload(pyarrow_module)

    from rayforce.plugins.pyarrow import from_arrow

    class MockTable:
        pass

    with pytest.raises(ImportError, match="pyarrow is required"):
        from_arrow(MockTable())

    # Restore original pyarrow if it existed
    if original_pyarrow:
        sys.modules["pyarrow"] = original_pyarrow


def test_from_arrow_multiple_chunks(pyarrow):
    # ChunkedArray with >1 chunk must be combined before buffer access.
    chunked = pyarrow.chunked_array(
        [pyarrow.array([1, 2], pyarrow.int64()), pyarrow.array([3, 4], pyarrow.int64())]
    )
    table = pyarrow.table({"id": chunked})
    assert table["id"].num_chunks == 2

    result = from_arrow(table)
    assert_table_shape(result, rows=4, cols=1)
    assert_column_values(result, "id", [1, 2, 3, 4])


def test_from_arrow_mixed_types(pyarrow):
    table = pyarrow.table(
        {
            "id": pyarrow.array([1, 2, 3, 4, 5], pyarrow.int64()),
            "name": pyarrow.array(["Alice", "Bob", "Charlie", "Diana", "Eve"], pyarrow.string()),
            "age": pyarrow.array([25, 30, 35, 28, 32], pyarrow.int64()),
            "salary": pyarrow.array(
                [50000.0, 60000.0, 70000.0, 55000.0, 65000.0], pyarrow.float64()
            ),
            "active": pyarrow.array([True, True, False, True, False], pyarrow.bool_()),
            "hire_date": pyarrow.array(
                [
                    dt.datetime(2020, 1, 1, tzinfo=dt.UTC),
                    dt.datetime(2019, 6, 15, tzinfo=dt.UTC),
                    dt.datetime(2018, 3, 20, tzinfo=dt.UTC),
                    dt.datetime(2021, 9, 10, tzinfo=dt.UTC),
                    dt.datetime(2017, 12, 5, tzinfo=dt.UTC),
                ],
                pyarrow.timestamp("us", tz="UTC"),
            ),
        }
    )

    result = from_arrow(table)

    assert_table_shape(result, rows=5, cols=6)

    values = result.values()
    assert all(isinstance(v, I64) for v in values[0])  # id
    assert all(isinstance(v, String) for v in values[1])  # name
    assert all(isinstance(v, I64) for v in values[2])  # age
    assert all(isinstance(v, F64) for v in values[3])  # salary
    assert all(isinstance(v, B8) for v in values[4])  # active
    assert all(isinstance(v, Timestamp) for v in values[5] if v is not None)  # hire_date


def test_from_arrow_large_table(pyarrow):
    n_rows = 1000
    table = pyarrow.table(
        {
            "id": pyarrow.array(list(range(n_rows)), pyarrow.int64()),
            "value": pyarrow.array([float(i) * 1.5 for i in range(n_rows)], pyarrow.float64()),
            "label": pyarrow.array([f"item_{i}" for i in range(n_rows)], pyarrow.string()),
        }
    )

    result = from_arrow(table)

    assert_table_shape(result, rows=n_rows, cols=3)

    values = result.values()
    assert values[0][0].value == 0
    assert values[0][-1].value == n_rows - 1


def test_from_arrow_single_column(pyarrow):
    table = pyarrow.table({"single_col": pyarrow.array([1, 2, 3, 4, 5], pyarrow.int64())})

    result = from_arrow(table)
    assert_table_shape(result, rows=5, cols=1)


def test_from_arrow_single_row(pyarrow):
    table = pyarrow.table(
        {
            "id": pyarrow.array([1], pyarrow.int64()),
            "name": pyarrow.array(["Alice"], pyarrow.string()),
            "value": pyarrow.array([10.5], pyarrow.float64()),
        }
    )

    result = from_arrow(table)
    assert_table_shape(result, rows=1, cols=3)
