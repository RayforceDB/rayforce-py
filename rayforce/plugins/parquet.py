"""
Parquet reading.

Reads a Parquet file into a ``pyarrow.Table`` and converts it to a Rayforce
``Table`` via the pyarrow plugin's shared conversion (which owns the
Arrow->Ray type mapping and zero-copy buffer fast path). Unlike ``from_arrow``,
this allows schema-only files with zero rows.
"""

from __future__ import annotations

from pathlib import Path
import sys
import typing as t

from rayforce.plugins.pyarrow import _table_from_arrow

if t.TYPE_CHECKING:
    from rayforce.types import Table


def load_parquet(path: str) -> Table:
    try:
        import pyarrow as pa  # type: ignore[import-not-found]
        from pyarrow import parquet as pq  # type: ignore[import-not-found]
    except ImportError as e:
        raise ImportError(
            "pyarrow is required for load_parquet(). Install it with: pip install pyarrow"
        ) from e

    _path = Path(path).absolute()
    if sys.stdout.isatty():
        sys.stdout.write(f"Reading {_path} ({(_path.stat().st_size / (1024 * 1024)):.2f} MB)\n")
        sys.stdout.flush()

    return _table_from_arrow(pa, pq.read_table(_path))
