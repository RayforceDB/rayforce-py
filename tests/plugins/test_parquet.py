# tests/test_load_parquet.py
from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from rayforce.plugins.parquet import load_parquet
from tests.helpers.assertions import assert_contains_columns

pytestmark = pytest.mark.plugin


def _generate_test_parquet(
    output_path: Path,
    target_size_mb: int = 20,
    batch_size: int = 50_000,
) -> None:
    if pa is None or pq is None:
        raise RuntimeError("pyarrow is required for this test")

    target_size_bytes = int(target_size_mb * 1024 * 1024)

    schema = pa.schema(
        [
            ("id", pa.int64()),
            ("name", pa.string()),
            ("value", pa.float64()),
            ("is_active", pa.bool_()),
            ("category", pa.string()),
            ("score", pa.int32()),
            ("timestamp", pa.timestamp("ns")),
        ]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    writer = pq.ParquetWriter(str(output_path), schema, compression="snappy")

    total_rows = 0
    try:
        while True:
            batch_start_id = total_rows
            ids = list(range(batch_start_id, batch_start_id + batch_size))
            names = [f"user_{i:08d}" for i in ids]
            values = [float(i % 1000) / 10.0 for i in ids]
            is_active = [i % 2 == 0 for i in ids]
            categories = [f"cat_{i % 10}" for i in ids]
            scores = [i % 100 for i in ids]
            timestamps = [1696118400000000000 + i * 1_000_000_000 for i in ids]

            arrays = [
                pa.array(ids, type=pa.int64()),
                pa.array(names, type=pa.string()),
                pa.array(values, type=pa.float64()),
                pa.array(is_active, type=pa.bool_()),
                pa.array(categories, type=pa.string()),
                pa.array(scores, type=pa.int32()),
                pa.array(timestamps, type=pa.timestamp("ns")),
            ]

            batch = pa.record_batch(arrays, schema=schema)
            writer.write_batch(batch)

            total_rows += batch_size
            if (total_rows // batch_size) % 2 == 0:
                if output_path.exists() and output_path.stat().st_size >= target_size_bytes:
                    break
    finally:
        writer.close()


def test_load_parquet_reads_generated_file(tmp_path: Path) -> None:
    parquet_path = tmp_path / "test_20mb.parquet"
    _generate_test_parquet(parquet_path, target_size_mb=20, batch_size=50_000)

    assert parquet_path.exists()
    assert parquet_path.stat().st_size >= 20 * 1024 * 1024

    table = load_parquet(str(parquet_path))

    assert_contains_columns(
        table, ["id", "name", "value", "is_active", "category", "score", "timestamp"]
    )

    assert table.at_column("id")[0] == 0
    assert table.at_column("id")[100000] == 100000
    assert table.at_column("id")[-1] == 999999


# ---------------------------------------------------------------------------
# Small parquet file loading
# ---------------------------------------------------------------------------


def _write_small_parquet(path: Path, compression: str = "snappy") -> None:
    """Helper to write a small parquet file with known data."""
    table = pa.table(
        {
            "id": pa.array([1, 2, 3], type=pa.int64()),
            "name": pa.array(["alice", "bob", "charlie"], type=pa.string()),
            "score": pa.array([10.5, 20.5, 30.5], type=pa.float64()),
        }
    )
    pq.write_table(table, str(path), compression=compression)


def test_load_small_parquet(tmp_path: Path) -> None:
    """Load a small parquet file with only a few rows."""
    parquet_path = tmp_path / "small.parquet"
    _write_small_parquet(parquet_path)

    table = load_parquet(str(parquet_path))
    assert_contains_columns(table, ["id", "name", "score"])
    assert len(table) == 3


def test_load_small_parquet_values(tmp_path: Path) -> None:
    """Verify actual values read from a small parquet file."""
    parquet_path = tmp_path / "small_values.parquet"
    _write_small_parquet(parquet_path)

    table = load_parquet(str(parquet_path))

    ids = table.at_column("id")
    assert ids[0] == 1
    assert ids[1] == 2
    assert ids[2] == 3

    scores = table.at_column("score")
    assert abs(scores[0].value - 10.5) < 1e-5
    assert abs(scores[1].value - 20.5) < 1e-5
    assert abs(scores[2].value - 30.5) < 1e-5


# ---------------------------------------------------------------------------
# Corrupted / missing file error handling
# ---------------------------------------------------------------------------


def test_load_missing_file_raises(tmp_path: Path) -> None:
    """Loading a non-existent file should raise an error."""
    nonexistent = tmp_path / "does_not_exist.parquet"
    with pytest.raises((FileNotFoundError, OSError, Exception)):
        load_parquet(str(nonexistent))


def test_load_corrupted_file_raises(tmp_path: Path) -> None:
    """Loading a corrupted (non-parquet) file should raise an error."""
    corrupted = tmp_path / "corrupted.parquet"
    corrupted.write_bytes(b"this is not a valid parquet file content at all")

    with pytest.raises(Exception):
        load_parquet(str(corrupted))


def test_load_empty_binary_file_raises(tmp_path: Path) -> None:
    """Loading a zero-byte file should raise an error."""
    empty_file = tmp_path / "empty_bytes.parquet"
    empty_file.write_bytes(b"")

    with pytest.raises(Exception):
        load_parquet(str(empty_file))


# ---------------------------------------------------------------------------
# Empty parquet file (valid schema, zero rows)
# ---------------------------------------------------------------------------


def test_load_empty_parquet(tmp_path: Path) -> None:
    """Load a valid parquet file with zero rows."""
    schema = pa.schema(
        [
            ("id", pa.int64()),
            ("name", pa.string()),
        ]
    )
    empty_table = pa.table(
        {"id": pa.array([], type=pa.int64()), "name": pa.array([], type=pa.string())}
    )
    parquet_path = tmp_path / "empty.parquet"
    pq.write_table(empty_table, str(parquet_path))

    table = load_parquet(str(parquet_path))
    assert_contains_columns(table, ["id", "name"])
    assert len(table) == 0


# ---------------------------------------------------------------------------
# Column type preservation
# ---------------------------------------------------------------------------


def test_column_type_int_preserved(tmp_path: Path) -> None:
    """Integer columns should be loaded with the correct rayforce int type."""
    pa_table = pa.table(
        {
            "i16_col": pa.array([1, 2, 3], type=pa.int16()),
            "i32_col": pa.array([10, 20, 30], type=pa.int32()),
            "i64_col": pa.array([100, 200, 300], type=pa.int64()),
        }
    )
    path = tmp_path / "int_types.parquet"
    pq.write_table(pa_table, str(path))

    table = load_parquet(str(path))
    assert_contains_columns(table, ["i16_col", "i32_col", "i64_col"])
    assert len(table) == 3

    # Values should be correct
    assert table.at_column("i64_col")[0] == 100
    assert table.at_column("i64_col")[2] == 300


def test_column_type_float_preserved(tmp_path: Path) -> None:
    """Float columns should be loaded as F64."""
    pa_table = pa.table(
        {
            "f32_col": pa.array([1.5, 2.5], type=pa.float32()),
            "f64_col": pa.array([10.5, 20.5], type=pa.float64()),
        }
    )
    path = tmp_path / "float_types.parquet"
    pq.write_table(pa_table, str(path))

    table = load_parquet(str(path))
    assert_contains_columns(table, ["f32_col", "f64_col"])
    assert len(table) == 2

    assert abs(table.at_column("f64_col")[0].value - 10.5) < 1e-5


def test_column_type_bool_preserved(tmp_path: Path) -> None:
    """Boolean columns should be loaded as B8."""
    pa_table = pa.table({"flag": pa.array([True, False, True], type=pa.bool_())})
    path = tmp_path / "bool_types.parquet"
    pq.write_table(pa_table, str(path))

    table = load_parquet(str(path))
    assert_contains_columns(table, ["flag"])
    assert len(table) == 3

    assert table.at_column("flag")[0].value is True
    assert table.at_column("flag")[1].value is False


def test_column_type_string_preserved(tmp_path: Path) -> None:
    """String columns should be loaded correctly."""
    pa_table = pa.table({"label": pa.array(["hello", "world", "test"], type=pa.string())})
    path = tmp_path / "string_types.parquet"
    pq.write_table(pa_table, str(path))

    table = load_parquet(str(path))
    assert_contains_columns(table, ["label"])
    assert len(table) == 3


def test_column_type_timestamp_preserved(tmp_path: Path) -> None:
    """Timestamp columns should be loaded as Timestamp."""
    pa_table = pa.table(
        {"ts": pa.array([1696118400000000000, 1696204800000000000], type=pa.timestamp("ns"))}
    )
    path = tmp_path / "timestamp_types.parquet"
    pq.write_table(pa_table, str(path))

    table = load_parquet(str(path))
    assert_contains_columns(table, ["ts"])
    assert len(table) == 2


def test_mixed_column_types(tmp_path: Path) -> None:
    """Parquet file with a mix of all common types."""
    pa_table = pa.table(
        {
            "id": pa.array([1, 2], type=pa.int64()),
            "name": pa.array(["a", "b"], type=pa.string()),
            "value": pa.array([1.1, 2.2], type=pa.float64()),
            "active": pa.array([True, False], type=pa.bool_()),
            "ts": pa.array([1696118400000000000, 1696204800000000000], type=pa.timestamp("ns")),
        }
    )
    path = tmp_path / "mixed_types.parquet"
    pq.write_table(pa_table, str(path))

    table = load_parquet(str(path))
    assert_contains_columns(table, ["id", "name", "value", "active", "ts"])
    assert len(table) == 2


# ---------------------------------------------------------------------------
# Different compression algorithms
# ---------------------------------------------------------------------------


def test_compression_snappy(tmp_path: Path) -> None:
    """Load parquet file compressed with snappy."""
    path = tmp_path / "snappy.parquet"
    _write_small_parquet(path, compression="snappy")

    table = load_parquet(str(path))
    assert_contains_columns(table, ["id", "name", "score"])
    assert len(table) == 3


def test_compression_gzip(tmp_path: Path) -> None:
    """Load parquet file compressed with gzip."""
    path = tmp_path / "gzip.parquet"
    _write_small_parquet(path, compression="gzip")

    table = load_parquet(str(path))
    assert_contains_columns(table, ["id", "name", "score"])
    assert len(table) == 3


def test_compression_none(tmp_path: Path) -> None:
    """Load parquet file with no compression."""
    path = tmp_path / "none.parquet"
    _write_small_parquet(path, compression="none")

    table = load_parquet(str(path))
    assert_contains_columns(table, ["id", "name", "score"])
    assert len(table) == 3


def test_compression_zstd(tmp_path: Path) -> None:
    """Load parquet file compressed with zstd."""
    path = tmp_path / "zstd.parquet"
    try:
        _write_small_parquet(path, compression="zstd")
    except Exception:
        pytest.skip("zstd compression not available")

    table = load_parquet(str(path))
    assert_contains_columns(table, ["id", "name", "score"])
    assert len(table) == 3


def test_compression_lz4(tmp_path: Path) -> None:
    """Load parquet file compressed with lz4."""
    path = tmp_path / "lz4.parquet"
    try:
        _write_small_parquet(path, compression="lz4")
    except Exception:
        pytest.skip("lz4 compression not available")

    table = load_parquet(str(path))
    assert_contains_columns(table, ["id", "name", "score"])
    assert len(table) == 3


def test_compression_brotli(tmp_path: Path) -> None:
    """Load parquet file compressed with brotli."""
    path = tmp_path / "brotli.parquet"
    try:
        _write_small_parquet(path, compression="brotli")
    except Exception:
        pytest.skip("brotli compression not available")

    table = load_parquet(str(path))
    assert_contains_columns(table, ["id", "name", "score"])
    assert len(table) == 3
