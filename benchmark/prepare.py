import duckdb
import numpy as np
import pandas as pd
import polars as pl

from rayforce import F64, I64, Table, Vector


def convert_to_vectors(data):
    """
    Convert numpy arrays to Vector objects for Rayforce Table.
    """

    result = {}
    for key, value in data.items():
        values_list = value.tolist() if isinstance(value, np.ndarray) else list(value)

        # Determine ray type based on column name or data type
        if key.startswith("id"):
            # ID columns are integers
            result[key] = Vector(items=values_list, ray_type=I64)
        elif key.startswith("v"):
            # Value columns are floats
            result[key] = Vector(items=values_list, ray_type=F64)
        # Default: infer from first value
        elif values_list and isinstance(values_list[0], (int, np.integer)):
            result[key] = Vector(items=values_list, ray_type=I64)
        elif values_list and isinstance(values_list[0], (float, np.floating)):
            result[key] = Vector(items=values_list, ray_type=F64)
        else:
            # Fallback to I64 if we can't determine
            result[key] = Vector(items=values_list, ray_type=I64)

    return result


def generate_test_data(n_rows=1_000_000, n_groups=100):
    """
    Generate test data for H2OAI benchmark.
    """

    np.random.seed(42)

    return {
        "id1": np.random.randint(1, n_groups + 1, n_rows),
        "id2": np.random.randint(1, n_groups + 1, n_rows),
        "id3": np.random.randint(1, n_groups + 1, n_rows),
        "v1": np.random.randn(n_rows),
        "v2": np.random.randn(n_rows),
        "v3": np.random.randn(n_rows),
    }


def prepare_data():
    data = generate_test_data()

    # Prepare pandas DF
    df = pd.DataFrame(data)

    # Prepare Polars DF
    pl_df = pl.DataFrame(data)

    # Prepare DuckDB connection with native table (faster than registered pandas df)
    duck_conn = duckdb.connect()
    duck_conn.register("_temp_df", df)
    duck_conn.execute("CREATE TABLE df AS SELECT * FROM _temp_df")

    # Prepare Rayforce-Py table
    table = Table(convert_to_vectors(data))

    # Prepare Rayforce table (used in runtime)
    table.save("t")

    return df, pl_df, duck_conn, table
