import datetime as dt

import pytest

from rayforce.plugins.polars import from_polars
from rayforce.types import B8, F64, I16, I32, I64, Symbol, Table, Date, Timestamp


@pytest.fixture
def polars():
    try:
        import polars as pl

        return pl
    except ImportError:
        pytest.skip("polars is not installed")


def test_from_polars_basic_types(polars):
    df = polars.DataFrame(
        {
            "bool_col": [True, False, True],
            "i8_col": [1, 2, 3],
            "i16_col": [100, 200, 300],
            "i32_col": [1000, 2000, 3000],
            "i64_col": [10000, 20000, 30000],
            "f32_col": [1.5, 2.5, 3.5],
            "f64_col": [10.5, 20.5, 30.5],
            "str_col": ["a", "b", "c"],
        },
        schema={
            "bool_col": polars.Boolean,
            "i8_col": polars.Int8,
            "i16_col": polars.Int16,
            "i32_col": polars.Int32,
            "i64_col": polars.Int64,
            "f32_col": polars.Float32,
            "f64_col": polars.Float64,
            "str_col": polars.String,
        },
    )

    table = from_polars(df)

    assert isinstance(table, Table)
    assert len(table.columns()) == 8

    # Check column names
    columns = [str(col) for col in table.columns()]
    assert "bool_col" in columns
    assert "i8_col" in columns
    assert "i16_col" in columns
    assert "i32_col" in columns
    assert "i64_col" in columns
    assert "f32_col" in columns
    assert "f64_col" in columns
    assert "str_col" in columns


def test_from_polars_boolean_type(polars):
    df = polars.DataFrame({"bool_col": [True, False, True]}, schema={"bool_col": polars.Boolean})
    table = from_polars(df)

    values = table.values()
    assert len(values) == 1
    bool_vector = values[0]

    # Check that values are B8 type
    assert all(isinstance(v, B8) for v in bool_vector)
    assert [v.value for v in bool_vector] == [True, False, True]


def test_from_polars_integer_types(polars):
    df = polars.DataFrame(
        {
            "i8": [1, 2, 3],
            "i16": [100, 200, 300],
            "i32": [1000, 2000, 3000],
            "i64": [10000, 20000, 30000],
        },
        schema={
            "i8": polars.Int8,
            "i16": polars.Int16,
            "i32": polars.Int32,
            "i64": polars.Int64,
        },
    )

    table = from_polars(df)
    values = table.values()

    # i8 -> I16
    assert all(isinstance(v, I16) for v in values[0])
    assert [v.value for v in values[0]] == [1, 2, 3]

    # i16 -> I16
    assert all(isinstance(v, I16) for v in values[1])
    assert [v.value for v in values[1]] == [100, 200, 300]

    # i32 -> I32
    assert all(isinstance(v, I32) for v in values[2])
    assert [v.value for v in values[2]] == [1000, 2000, 3000]

    # i64 -> I64
    assert all(isinstance(v, I64) for v in values[3])
    assert [v.value for v in values[3]] == [10000, 20000, 30000]


def test_from_polars_float_types(polars):
    df = polars.DataFrame(
        {
            "f32": [1.5, 2.5, 3.5],
            "f64": [10.5, 20.5, 30.5],
        },
        schema={
            "f32": polars.Float32,
            "f64": polars.Float64,
        },
    )

    table = from_polars(df)
    values = table.values()

    for vector in values:
        assert all(isinstance(v, F64) for v in vector)

    assert [round(v.value, 1) for v in values[0]] == [1.5, 2.5, 3.5]
    assert [round(v.value, 1) for v in values[1]] == [10.5, 20.5, 30.5]


def test_from_polars_string_types(polars):
    """Test string type conversions."""
    from rayforce.plugins.polars import from_polars
    from rayforce.types import Symbol

    df = polars.DataFrame(
        {
            "str_col": ["a", "b", "c"],
            "string_col": ["x", "y", "z"],
        },
        schema={
            "str_col": polars.String,
            "string_col": polars.String,
        },
    )

    table = from_polars(df)
    values = table.values()

    for vector in values:
        assert all(isinstance(v, Symbol) for v in vector)

    assert [v.value for v in values[0]] == ["a", "b", "c"]
    assert [v.value for v in values[1]] == ["x", "y", "z"]


def test_from_polars_datetime_types(polars):
    dates = [dt.date(2023, 1, 1), dt.date(2023, 1, 2), dt.date(2023, 1, 3)]
    datetimes = [
        dt.datetime(2023, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc),
        dt.datetime(2023, 1, 2, 12, 0, 0, tzinfo=dt.timezone.utc),
        dt.datetime(2023, 1, 3, 12, 0, 0, tzinfo=dt.timezone.utc),
    ]

    df = polars.DataFrame(
        {
            "date_col": dates,
            "datetime_col": datetimes,
        },
        schema={
            "date_col": polars.Date,
            "datetime_col": polars.Datetime(time_unit="us", time_zone=None),
        },
    )

    table = from_polars(df)
    values = table.values()

    # Date column
    assert all(isinstance(v, Date) for v in values[0] if v is not None)
    assert [v.value for v in values[0] if v is not None] == dates

    # Datetime column
    assert all(isinstance(v, Timestamp) for v in values[1] if v is not None)
    assert len(values[1]) == 3


def test_from_polars_with_nulls(polars):
    df = polars.DataFrame(
        {
            "int_col": [1, None, 3],
            "float_col": [1.5, None, 3.5],
            "string_col": ["a", None, "c"],
            "bool_col": [True, None, False],
        }
    )

    table = from_polars(df)
    values = table.values()

    # Check that nulls are handled (polars already converts to None)
    int_vector = values[0]
    assert int_vector[0].value == 1
    assert int_vector[1] == []  # TODO: Subject to change one Null is introduced to rf
    assert int_vector[2].value == 3

    float_vector = values[1]
    assert float_vector[0].value == 1.5
    assert float_vector[1] == []  # TODO: Subject to change one Null is introduced to rf
    assert float_vector[2].value == 3.5


def test_from_polars_empty_dataframe_raises(polars):
    df = polars.DataFrame()

    with pytest.raises(ValueError, match="Cannot convert empty DataFrame"):
        from_polars(df)


def test_from_polars_wrong_type_raises():
    with pytest.raises(TypeError, match="Expected polars.DataFrame"):
        from_polars("not a dataframe")


def test_from_polars_missing_dependency(monkeypatch):
    from rayforce.plugins import polars as polars_module

    import sys

    original_polars = sys.modules.get("polars")
    if "polars" in sys.modules:
        del sys.modules["polars"]

    original_import = __import__

    def mock_import(name, *args, **kwargs):
        if name == "polars":
            raise ImportError("No module named 'polars'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", mock_import)

    import importlib

    importlib.reload(polars_module)

    from rayforce.plugins.polars import from_polars

    class MockDF:
        pass

    with pytest.raises(ImportError, match="polars is required"):
        from_polars(MockDF())

    # Restore original polars if it existed
    if original_polars:
        sys.modules["polars"] = original_polars


def test_from_polars_dtype_name_inference(polars):
    df = polars.DataFrame(
        {
            "bool": [True, False],
            "i8": [1, 2],
            "i16": [100, 200],
            "i32": [1000, 2000],
            "i64": [10000, 20000],
            "f32": [1.5, 2.5],
            "f64": [10.5, 20.5],
            "str": ["a", "b"],
        },
        schema={
            "bool": polars.Boolean,
            "i8": polars.Int8,
            "i16": polars.Int16,
            "i32": polars.Int32,
            "i64": polars.Int64,
            "f32": polars.Float32,
            "f64": polars.Float64,
            "str": polars.String,
        },
    )

    table = from_polars(df)
    values = table.values()

    assert all(isinstance(v, B8) for v in values[0])  # Boolean
    assert all(isinstance(v, I16) for v in values[1])  # Int8
    assert all(isinstance(v, I16) for v in values[2])  # Int16
    assert all(isinstance(v, I32) for v in values[3])  # Int32
    assert all(isinstance(v, I64) for v in values[4])  # Int64
    assert all(isinstance(v, F64) for v in values[5])  # Float32
    assert all(isinstance(v, F64) for v in values[6])  # Float64
    assert all(isinstance(v, Symbol) for v in values[7])  # String


def test_from_polars_mixed_types(polars):
    df = polars.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "age": [25, 30, 35, 28, 32],
            "salary": [50000.0, 60000.0, 70000.0, 55000.0, 65000.0],
            "active": [True, True, False, True, False],
            "hire_date": [
                dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
                dt.datetime(2019, 6, 15, tzinfo=dt.timezone.utc),
                dt.datetime(2018, 3, 20, tzinfo=dt.timezone.utc),
                dt.datetime(2021, 9, 10, tzinfo=dt.timezone.utc),
                dt.datetime(2017, 12, 5, tzinfo=dt.timezone.utc),
            ],
        },
        schema={
            "id": polars.Int64,
            "name": polars.String,
            "age": polars.Int64,
            "salary": polars.Float64,
            "active": polars.Boolean,
            "hire_date": polars.Datetime(time_unit="us", time_zone=None),
        },
    )

    table = from_polars(df)

    assert isinstance(table, Table)
    assert len(table.columns()) == 6

    values = table.values()

    assert all(isinstance(v, I64) for v in values[0])  # id
    assert all(isinstance(v, Symbol) for v in values[1])  # name
    assert all(isinstance(v, I64) for v in values[2])  # age
    assert all(isinstance(v, F64) for v in values[3])  # salary
    assert all(isinstance(v, B8) for v in values[4])  # active
    assert all(isinstance(v, Timestamp) for v in values[5] if v is not None)  # hire_date


def test_from_polars_large_dataframe(polars):
    n_rows = 1000
    df = polars.DataFrame(
        {
            "id": list(range(n_rows)),
            "value": [float(i) * 1.5 for i in range(n_rows)],
            "label": [f"item_{i}" for i in range(n_rows)],
        }
    )

    table = from_polars(df)

    assert isinstance(table, Table)
    assert len(table.columns()) == 3

    values = table.values()
    assert len(values[0]) == n_rows
    assert len(values[1]) == n_rows
    assert len(values[2]) == n_rows

    assert values[0][0].value == 0
    assert values[0][-1].value == n_rows - 1


def test_from_polars_single_column(polars):
    df = polars.DataFrame({"single_col": [1, 2, 3, 4, 5]})

    table = from_polars(df)

    assert isinstance(table, Table)
    assert len(table.columns()) == 1
    assert len(table.values()[0]) == 5


def test_from_polars_single_row(polars):
    df = polars.DataFrame(
        {
            "id": [1],
            "name": ["Alice"],
            "value": [10.5],
        }
    )

    table = from_polars(df)

    assert isinstance(table, Table)
    assert len(table.columns()) == 3
    assert len(table.values()[0]) == 1


def test_from_polars_string_fallback(polars):
    df = polars.DataFrame({"col": ["a", "b", "c"]})

    table = from_polars(df)
    values = table.values()

    assert all(isinstance(v, Symbol) for v in values[0])


def test_from_polars_all_null_column(polars):
    df = polars.DataFrame(
        {
            "null_int": [None, None, None],
            "null_str": [None, None, None],
            "mixed": [1, None, 3],
        }
    )

    table = from_polars(df)
    values = table.values()

    assert len(values[0]) == 3

    assert values[2][0].value == 1
    assert values[2][1] == []
    assert values[2][2].value == 3
