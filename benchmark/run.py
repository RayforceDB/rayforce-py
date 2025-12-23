from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import statistics

import benchmarks
import format
import prepare


def run(n_runs=15, n_warmup=5, mode="light"):
    """
    Run benchmarks with specified number of runs.

    Args:
        n_runs: Number of benchmark runs per query (default: 15)
        n_warmup: Number of warmup runs per query (default: 5)
        mode: Benchmark mode - "light" (Q1-Q6) or "full" (Q1-Q7) (default: "light")
    """
    print("Running benchmarks...")
    print("Preparing data...")
    pandas_df, polars_df, rayforce_table = prepare.prepare_data()

    # Filter benchmarks based on mode
    if mode == "light":
        benchmark_list = benchmarks.benchmarks[:-1]  # Q1-Q6
    elif mode == "full":
        benchmark_list = benchmarks.benchmarks  # Q1-Q7
    else:
        raise ValueError(f"Invalid mode: {mode}. Must be 'light' or 'full'")

    # Open results file for writing
    results_file = open("results.txt", "w")

    format.intro(results_file)
    results_file.write(f"\nDataset: {len(pandas_df):,} rows, {len(pandas_df.columns)} columns\n")
    results_file.write(f"Mode: {mode}\n")
    results_file.write(f"Runs per query: {n_runs} (median)\n")
    results_file.write(f"Warmup runs: {n_warmup}\n")
    results_file.write("-" * 70 + "\n")

    results = []

    for benchmark_tuple in benchmark_list:
        if len(benchmark_tuple) == 6:
            (
                query_name,
                rayforce_py_func,
                pandas_func,
                polars_func,
                polars_streaming_func,
                native_rayforce_func,
            ) = benchmark_tuple
        else:
            # Backward compatibility - old format without streaming
            query_name, rayforce_py_func, pandas_func, polars_func, native_rayforce_func = (
                benchmark_tuple
            )
            polars_streaming_func = None
        print(f"\nRunning {query_name}...")

        # Check if this is Q7 - run only once, no warmup
        is_q7 = query_name.startswith("Q7:")

        if not is_q7:
            # Warmup runs (skip for Q7)
            for _ in range(n_warmup):
                rayforce_py_func(rayforce_table)
                pandas_func(pandas_df)
                polars_func(polars_df)
                if polars_streaming_func:
                    polars_streaming_func(polars_df)
                native_rayforce_func("t")

            rayforce_py_times = []
            pandas_times = []
            polars_times = []
            polars_streaming_times = []
            native_rayforce_times = []

            # Actual benchmark runs
            for i in range(n_runs):
                rf_py_time, _ = rayforce_py_func(rayforce_table)
                pd_time, _ = pandas_func(pandas_df)
                pl_time, _ = polars_func(polars_df)
                if polars_streaming_func:
                    pl_streaming_time, _ = polars_streaming_func(polars_df)
                    polars_streaming_times.append(pl_streaming_time)
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
            median_polars_streaming = (
                statistics.median(polars_streaming_times) if polars_streaming_times else 0
            )
            median_native_rayforce = statistics.median(native_rayforce_times)

            # Calculate standard deviation for reporting
            std_rayforce_py = (
                statistics.stdev(rayforce_py_times) if len(rayforce_py_times) > 1 else 0
            )
            std_pandas = statistics.stdev(pandas_times) if len(pandas_times) > 1 else 0
            std_polars = statistics.stdev(polars_times) if len(polars_times) > 1 else 0
            std_polars_streaming = (
                statistics.stdev(polars_streaming_times) if len(polars_streaming_times) > 1 else 0
            )
            std_native_rayforce = (
                statistics.stdev(native_rayforce_times) if len(native_rayforce_times) > 1 else 0
            )
        else:
            # Q7: Run only once, no warmup
            print(f"  Running {query_name} (single run, no warmup)...")
            rf_py_time, _ = rayforce_py_func(rayforce_table)
            pd_time, _ = pandas_func(pandas_df)
            pl_time, _ = polars_func(polars_df)
            if polars_streaming_func:
                pl_streaming_time, _ = polars_streaming_func(polars_df)
            else:
                pl_streaming_time = 0
            native_time, _ = native_rayforce_func("t")

            median_rayforce_py = rf_py_time
            median_pandas = pd_time
            median_polars = pl_time
            median_polars_streaming = pl_streaming_time
            median_native_rayforce = native_time

            std_rayforce_py = 0
            std_pandas = 0
            std_polars = 0
            std_polars_streaming = 0
            std_native_rayforce = 0

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
            polars_streaming_time=median_polars_streaming if polars_streaming_func else None,
            std_polars_streaming=std_polars_streaming if polars_streaming_func else None,
            file=results_file,
        )
        if polars_streaming_func:
            results.append(
                (
                    query_name,
                    median_rayforce_py,
                    median_pandas,
                    median_polars,
                    median_polars_streaming,
                    median_native_rayforce,
                    std_rayforce_py,
                    std_pandas,
                    std_polars,
                    std_polars_streaming,
                    std_native_rayforce,
                )
            )
        else:
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

    format.outro(results_file)
    format.results(results, results_file)
    results_file.close()

    print("\n✓ Benchmarks completed!")
    print("Results written to results.txt")


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
    parser.add_argument(
        "--mode",
        type=str,
        default="light",
        choices=["light", "full"],
        help="Benchmark mode: 'light' (Q1-Q6) or 'full' (Q1-Q7) (default: light)",
    )

    args = parser.parse_args()
    run(n_runs=args.runs, n_warmup=args.warmup, mode=args.mode)
