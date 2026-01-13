# :fontawesome-solid-table: Apache Parquet Integration

WIP
!!! warning "Beta Feature"
    Parquet support is currently in beta and may behave unexpectedly. Please report any issues you encounter.

Rayforce-py provides support for reading Apache Parquet files directly into Rayforce Tables using the `load_parquet()` function.

## Installation

Parquet support requires PyArrow. Install it with:

```bash
pip install rayforce-py[parquet]
```

Or install PyArrow directly:

```bash
pip install pyarrow>=10.0.0
```

## Quick Start

```python
from rayforce.plugins.parquet import load_parquet

# Load a parquet file into a Rayforce Table
table = load_parquet("data.parquet")

# Access columns
print(table.columns())
print(table.at_column("id"))
```

## API Reference

### `load_parquet(path: str) -> Table`

Reads a Parquet file and returns a Rayforce Table.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str` | Path to the Parquet file |

**Returns:** A `Table` object containing the data from the Parquet file.

**Raises:**

- `ImportError`: If PyArrow is not installed
- `ParquetConversionError`: If a column type cannot be converted

## Type Mapping

Parquet/Arrow types are automatically mapped to Rayforce types:

| Arrow Type | Rayforce Type |
|------------|---------------|
| `bool` | `B8` |
| `int8`, `uint8` | `U8` |
| `int16`, `uint16` | `I16` |
| `int32`, `uint32` | `I32` |
| `int64`, `uint64` | `I64` |
| `float32`, `float64` | `F64` |
| `string`, `large_string` | `String` |
| `timestamp`, `date64` | `Timestamp` |
| `date32` | `Date` |
| `time32` | `Time` |
| Other types | `String` (fallback) |

## Performance

The Parquet reader uses zero-copy data access where possible for optimal performance. For the following types, data is read directly from Arrow buffers without copying:

- `I16`, `I32`, `I64`
- `F64`
- `B8`, `U8`
- `Timestamp`
- `String`

For unsupported types or when zero-copy is not possible, the reader falls back to converting via Python lists.
