import datetime as dt

import pytest

from rayforce.plugins.pandas import from_pandas
from rayforce.types import B8, Date, F64, I16, I32, I64, Symbol, Table, Timestamp


@pytest.fixture
def pandas():
    try:
        import pandas as pd

        return pd
    except ImportError:
        pytest.skip("pandas is not installed")


def test_from_pandas_basic_types(pandas):
    df = pandas.DataFrame(
        {
            "bool_col": [True, False, True],
            "int8_col": pandas.array([1, 2, 3], dtype="int8"),
            "int16_col": pandas.array([100, 200, 300], dtype="int16"),
            "int32_col": pandas.array([1000, 2000, 3000], dtype="int32"),
            "int64_col": pandas.array([10000, 20000, 30000], dtype="int64"),
            "float32_col": pandas.array([1.5, 2.5, 3.5], dtype="float32"),
            "float64_col": pandas.array([10.5, 20.5, 30.5], dtype="float64"),
            "string_col": ["a", "b", "c"],
            "object_col": ["x", "y", "z"],
        }
    )

    table = from_pandas(df)

    assert isinstance(table, Table)
    assert len(table.columns()) == 9

    # Check column names
    columns = [str(col) for col in table.columns()]
    assert "bool_col" in columns
    assert "int8_col" in columns
    assert "int16_col" in columns
    assert "int32_col" in columns
    assert "int64_col" in columns
    assert "float32_col" in columns
    assert "float64_col" in columns
    assert "string_col" in columns
    assert "object_col" in columns


def test_from_pandas_boolean_type(pandas):
    df = pandas.DataFrame({"bool_col": [True, False, True]})
    table = from_pandas(df)

    values = table.values()
    assert len(values) == 1
    bool_vector = values[0]

    assert all(isinstance(v, B8) for v in bool_vector)
    assert [v.value for v in bool_vector] == [True, False, True]


def test_from_pandas_integer_types(pandas):
    df = pandas.DataFrame(
        {
            "int8": pandas.array([1, 2, 3], dtype="int8"),
            "int16": pandas.array([100, 150, 200], dtype="int16"),
            "int32": pandas.array([1000, 1500, 2000], dtype="int32"),
            "int64": pandas.array([10000, 15000, 20000], dtype="int64"),
            "int_plain": [5, 6, 7],  # Default int (usually int64)
        }
    )

    table = from_pandas(df)
    values = table.values()

    # int8 -> I16
    assert all(isinstance(v, I16) for v in values[0])
    assert [v.value for v in values[0]] == [1, 2, 3]

    # int16 -> I16
    assert all(isinstance(v, I16) for v in values[1])
    assert [v.value for v in values[1]] == [100, 150, 200]

    # int32 -> I32
    assert all(isinstance(v, I32) for v in values[2])
    assert [v.value for v in values[2]] == [1000, 1500, 2000]

    # int64 -> I64
    assert all(isinstance(v, I64) for v in values[3])
    assert [v.value for v in values[3]] == [10000, 15000, 20000]

    # plain int -> I64 (default)
    assert all(isinstance(v, I64) for v in values[4])


def test_from_pandas_float_types(pandas):
    df = pandas.DataFrame(
        {
            "float32": pandas.array([1.5, 2.5, 3.5], dtype="float32"),
            "float64": pandas.array([10.5, 20.5, 30.5], dtype="float64"),
            "float_plain": [5.5, 6.5, 7.5],
        }
    )

    table = from_pandas(df)
    values = table.values()

    for vector in values:
        assert all(isinstance(v, F64) for v in vector)

    assert [round(v.value, 1) for v in values[0]] == [1.5, 2.5, 3.5]
    assert [round(v.value, 1) for v in values[1]] == [10.5, 20.5, 30.5]
    assert [round(v.value, 1) for v in values[2]] == [5.5, 6.5, 7.5]


def test_from_pandas_string_types(pandas):
    df = pandas.DataFrame(
        {
            "string_col": pandas.array(["a", "b", "c"], dtype="string"),
            "object_col": ["x", "y", "z"],
            "str_python": pandas.array(["foo", "bar", "baz"], dtype="string"),
        }
    )

    table = from_pandas(df)
    values = table.values()

    for vector in values:
        assert all(isinstance(v, Symbol) for v in vector)

    assert [v.value for v in values[0]] == ["a", "b", "c"]
    assert [v.value for v in values[1]] == ["x", "y", "z"]
    assert [v.value for v in values[2]] == ["foo", "bar", "baz"]


def test_from_pandas_datetime_types(pandas):
    dates = [dt.date(2023, 1, 1), dt.date(2023, 1, 2), dt.date(2023, 1, 3)]
    datetimes = [
        dt.datetime(2023, 1, 1, 12, 0, 0),
        dt.datetime(2023, 1, 2, 12, 0, 0),
        dt.datetime(2023, 1, 3, 12, 0, 0),
    ]

    datetime_series = pandas.to_datetime(datetimes)
    if hasattr(datetime_series, "tz") and datetime_series.tz is not None:
        datetime_series = datetime_series.tz_localize(None)
    elif hasattr(datetime_series, "dt") and datetime_series.dt.tz is not None:
        datetime_series = datetime_series.dt.tz_localize(None)

    df = pandas.DataFrame(
        {
            "date_col": dates,
            "datetime_col": datetime_series,
        }
    )

    table = from_pandas(df)
    values = table.values()

    # Date column
    assert all(isinstance(v, Date) for v in values[0] if v is not None)
    assert [v.value for v in values[0] if v is not None] == dates

    # Datetime column
    assert all(isinstance(v, Timestamp) for v in values[1] if v is not None)
    assert len(values[1]) == 3


def test_from_pandas_with_nulls(pandas):
    df = pandas.DataFrame(
        {
            "int_col": [1, None, 3],
            "float_col": [1.5, float("nan"), 3.5],
            "string_col": ["a", None, "c"],
            "bool_col": [True, None, False],
        }
    )

    table = from_pandas(df)
    values = table.values()

    int_vector = values[0]
    assert int_vector[0].value == 1
    assert int_vector[1] == []  # TODO: Subject to change one Null is introduced to rf
    assert int_vector[2].value == 3

    float_vector = values[1]
    assert float_vector[0].value == 1.5
    assert float_vector[1] == []  # TODO: Subject to change once Null is introduced to rf
    assert float_vector[2].value == 3.5


def test_from_pandas_datetime_with_nat(pandas):
    datetime_series = pandas.to_datetime(["2023-01-01", None, "2023-01-03"])
    if hasattr(datetime_series, "tz") and datetime_series.tz is not None:
        datetime_series = datetime_series.tz_localize(None)
    elif hasattr(datetime_series, "dt") and datetime_series.dt.tz is not None:
        datetime_series = datetime_series.dt.tz_localize(None)

    df = pandas.DataFrame({"datetime_col": datetime_series})

    table = from_pandas(df)
    values = table.values()

    datetime_vector = values[0]
    assert datetime_vector[0].value is not None
    assert datetime_vector[2].value is not None


def test_from_pandas_empty_dataframe_raises(pandas):
    df = pandas.DataFrame()

    with pytest.raises(ValueError, match="Cannot convert empty DataFrame"):
        from_pandas(df)


def test_from_pandas_wrong_type_raises():
    with pytest.raises(TypeError, match="Expected pandas.DataFrame"):
        from_pandas("not a dataframe")


def test_from_pandas_missing_dependency(monkeypatch):
    from rayforce.plugins import pandas as pandas_module

    import sys

    original_pandas = sys.modules.get("pandas")
    if "pandas" in sys.modules:
        del sys.modules["pandas"]

    original_import = __import__

    def mock_import(name, *args, **kwargs):
        if name == "pandas":
            raise ImportError("No module named 'pandas'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", mock_import)

    import importlib

    importlib.reload(pandas_module)

    from rayforce.plugins.pandas import from_pandas

    class MockDF:
        pass

    with pytest.raises(ImportError, match="pandas is required"):
        from_pandas(MockDF())

    # Restore original pandas if it existed
    if original_pandas:
        sys.modules["pandas"] = original_pandas


def test_from_pandas_dtype_kind_inference(pandas):
    df = pandas.DataFrame(
        {
            "bool_kind": [True, False, True],
            "int_kind": [1, 2, 3],
            "float_kind": [1.5, 2.5, 3.5],
            "object_kind": ["a", "b", "c"],
        }
    )

    table = from_pandas(df)
    values = table.values()

    assert all(isinstance(v, B8) for v in values[0])  # bool kind
    assert all(isinstance(v, I64) for v in values[1])  # int kind
    assert all(isinstance(v, F64) for v in values[2])  # float kind
    assert all(isinstance(v, Symbol) for v in values[3])  # object kind


def test_from_pandas_mixed_types(pandas):
    df = pandas.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "age": [25, 30, 35, 28, 32],
            "salary": [50000.0, 60000.0, 70000.0, 55000.0, 65000.0],
            "active": [True, True, False, True, False],
            "hire_date": pandas.to_datetime(
                ["2020-01-01", "2019-06-15", "2018-03-20", "2021-09-10", "2017-12-05"],
            ),
        }
    )

    table = from_pandas(df)

    assert isinstance(table, Table)
    assert len(table.columns()) == 6

    values = table.values()

    assert all(isinstance(v, I64) for v in values[0])  # id
    assert all(isinstance(v, Symbol) for v in values[1])  # name
    assert all(isinstance(v, I64) for v in values[2])  # age
    assert all(isinstance(v, F64) for v in values[3])  # salary
    assert all(isinstance(v, B8) for v in values[4])  # active
    assert all(isinstance(v, Timestamp) for v in values[5])  # hire_date


def test_from_pandas_large_dataframe(pandas):
    n_rows = 1000
    df = pandas.DataFrame(
        {
            "id": range(n_rows),
            "value": [float(i) * 1.5 for i in range(n_rows)],
            "label": [f"item_{i}" for i in range(n_rows)],
        }
    )

    table = from_pandas(df)

    assert isinstance(table, Table)
    assert len(table.columns()) == 3

    values = table.values()
    assert len(values[0]) == n_rows
    assert len(values[1]) == n_rows
    assert len(values[2]) == n_rows

    # Check first and last values
    assert values[0][0].value == 0
    assert values[0][-1].value == n_rows - 1


def test_from_pandas_single_column(pandas):
    df = pandas.DataFrame({"single_col": [1, 2, 3, 4, 5]})

    table = from_pandas(df)

    assert isinstance(table, Table)
    assert len(table.columns()) == 1
    assert len(table.values()[0]) == 5


def test_from_pandas_single_row(pandas):
    df = pandas.DataFrame(
        {
            "id": [1],
            "name": ["Alice"],
            "value": [10.5],
        }
    )

    table = from_pandas(df)

    assert isinstance(table, Table)
    assert len(table.columns()) == 3
    assert len(table.values()[0]) == 1
