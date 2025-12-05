import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import format
import prepare
import benchmarks
import statistics
import argparse


def run(n_runs=15, n_warmup=5):
    """
    Run benchmarks with specified number of runs.

    Args:
        n_runs: Number of benchmark runs per query (default: 15)
        n_warmup: Number of warmup runs per query (default: 5)
    """
    format.intro()

    print("Preparing data...")
    pandas_df, polars_df, rayforce_table = prepare.prepare_data()

    print(f"\nDataset: {len(pandas_df):,} rows, {len(pandas_df.columns)} columns")
    print(f"Runs per query: {n_runs} (median)")
    print(f"Warmup runs: {n_warmup}")
    print("-" * 70)

    results = []

    for (
        query_name,
        rayforce_py_func,
        pandas_func,
        polars_func,
        native_rayforce_func,
    ) in benchmarks.benchmarks:
        print(f"\nRunning {query_name}...")

        # Warmup runs
        for _ in range(n_warmup):
            rayforce_py_func(rayforce_table)
            pandas_func(pandas_df)
            polars_func(polars_df)
            native_rayforce_func("t")

        rayforce_py_times = []
        pandas_times = []
        polars_times = []
        native_rayforce_times = []

        # Actual benchmark runs
        for i in range(n_runs):
            rf_py_time, _ = rayforce_py_func(rayforce_table)
            pd_time, _ = pandas_func(pandas_df)
            pl_time, _ = polars_func(polars_df)
            native_time, _ = native_rayforce_func("t")
            rayforce_py_times.append(rf_py_time)
            pandas_times.append(pd_time)
            polars_times.append(pl_time)
            native_rayforce_times.append(native_time)

            # Progress indicator - show every 5 runs or on last run
            if (i + 1) % 5 == 0 or (i + 1) == n_runs:
                print(
                    f"  Completed {i + 1}/{n_runs} runs...",
                    end="\r" if (i + 1) < n_runs else "\n",
                )

        # Use median instead of mean for more robust results
        median_rayforce_py = statistics.median(rayforce_py_times)
        median_pandas = statistics.median(pandas_times)
        median_polars = statistics.median(polars_times)
        median_native_rayforce = statistics.median(native_rayforce_times)

        # Calculate standard deviation for reporting
        std_rayforce_py = (
            statistics.stdev(rayforce_py_times) if len(rayforce_py_times) > 1 else 0
        )
        std_pandas = statistics.stdev(pandas_times) if len(pandas_times) > 1 else 0
        std_polars = statistics.stdev(polars_times) if len(polars_times) > 1 else 0
        std_native_rayforce = (
            statistics.stdev(native_rayforce_times)
            if len(native_rayforce_times) > 1
            else 0
        )

        format.print_results(
            query_name,
            median_rayforce_py,
            median_pandas,
            median_polars,
            median_native_rayforce,
            std_rayforce_py,
            std_pandas,
            std_polars,
            std_native_rayforce,
        )
        results.append(
            (
                query_name,
                median_rayforce_py,
                median_pandas,
                median_polars,
                median_native_rayforce,
                std_rayforce_py,
                std_pandas,
                std_polars,
                std_native_rayforce,
            )
        )

    format.outro()
    format.results(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Rayforce-Py benchmarks")
    parser.add_argument(
        "--runs",
        type=int,
        default=15,
        help="Number of benchmark runs per query (default: 15)",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=5,
        help="Number of warmup runs per query (default: 5)",
    )

    args = parser.parse_args()
    run(n_runs=args.runs, n_warmup=args.warmup)
