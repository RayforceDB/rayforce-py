from rayforce import Table
import pandas as pd
import numpy as np


def convert_to_lists(data):
    """
    Convert numpy arrays to Python lists for Rayforce Table.
    """

    return {
        key: value.tolist() if isinstance(value, np.ndarray) else list(value)
        for key, value in data.items()
    }


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

    # Prepare Rayforce-Py table
    table = Table.from_dict(convert_to_lists(data))

    # Prepare Rayforce table (used in runtime)
    table.save("t")

    return df, table
