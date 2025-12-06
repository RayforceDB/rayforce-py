from rayforce import Table, Vector, I64, F64
import pandas as pd
import polars as pl
import numpy as np


def convert_to_vectors(data):
    """
    Convert numpy arrays to Vector objects for Rayforce Table.
    """

    result = {}
    for key, value in data.items():
        if isinstance(value, np.ndarray):
            values_list = value.tolist()
        else:
            values_list = list(value)
        
        # Determine ray type based on column name or data type
        if key.startswith("id"):
            # ID columns are integers
            result[key] = Vector(items=values_list, ray_type=I64)
        elif key.startswith("v"):
            # Value columns are floats
            result[key] = Vector(items=values_list, ray_type=F64)
        else:
            # Default: infer from first value
            if values_list and isinstance(values_list[0], (int, np.integer)):
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

    # Prepare Rayforce-Py table
    table = Table.from_dict(convert_to_vectors(data))

    # Prepare Rayforce table (used in runtime)
    table.save("t")

    return df, pl_df, table
