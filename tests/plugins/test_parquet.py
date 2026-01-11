# tests/test_load_parquet.py
from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from rayforce.plugins.parquet import load_parquet


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

    expected_cols = {"id", "name", "value", "is_active", "category", "score", "timestamp"}
    assert set(table.columns()) == expected_cols

    assert table.at_column("id")[0] == 0
    assert table.at_column("id")[100000] == 100000
    assert table.at_column("id")[-1] == 999999
