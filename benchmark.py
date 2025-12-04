"""
Benchmark comparing Rayforce-Py, Pandas, and native Rayforce performance.
Based on H2OAI benchmark queries from:
https://rayforcedb.com/content/benchmarks/bench.html?h=timeit#group-by-results
"""

import time
import pandas as pd
import numpy as np
from rayforce import Table, eval_str, I64, F64, Symbol, Vector, List


def print_results(query_name, rayforce_py_time, pandas_time, native_rayforce_time):
    """Print benchmark results in a formatted table."""
    print(f"\n{query_name}:")
    print(f"  Rayforce-Py:    {rayforce_py_time:,.2f} μs")
    print(f"  Pandas:         {pandas_time:,.2f} μs")
    print(f"  Native Rayforce: {native_rayforce_time:,.2f} μs")
    
    if native_rayforce_time > 0:
        speedup_vs_native = native_rayforce_time / rayforce_py_time if rayforce_py_time > 0 else 0
        print(f"  Rayforce-Py vs Native: {speedup_vs_native:.2f}x")
    
    speedup_vs_pandas = pandas_time / rayforce_py_time if rayforce_py_time > 0 else 0
    print(f"  Rayforce-Py vs Pandas: {speedup_vs_pandas:.2f}x")


def main():
    print("=" * 70)
    print("Rayforce-Py vs Pandas vs Rayforce Benchmark")
    print("Based on H2OAI Group By Benchmark")
    print("=" * 70)

    data = generate_test_data(n_rows=1_000_000, n_groups=100)
    
    # Create pandas DataFrame
    print("Creating pandas DataFrame...")
    df = pd.DataFrame(data)
    
    # Create Rayforce Table (convert numpy arrays to lists)
    print("Creating Rayforce-Py Table...")
    rayforce_data = convert_to_lists(data)
    table = Table.from_dict(rayforce_data)
    
    # Create native Rayforce table using eval_str
    print("Creating native Rayforce table...")
    table_name = "t"
    # Save the table to Rayforce runtime so we can reference it by name
    table.save(table_name)
    
    print(f"\nDataset: {len(df):,} rows, {len(df.columns)} columns")
    print("-" * 70)
    
    # Run benchmarks
    benchmarks = [
        ("Q1: Group by id1, sum v1", benchmark_q1_rayforce, benchmark_q1_pandas, benchmark_q1_native_rayforce),
        ("Q2: Group by id1, id2, sum v1", benchmark_q2_rayforce, benchmark_q2_pandas, benchmark_q2_native_rayforce),
        ("Q3: Group by id3, sum v1, avg v3", benchmark_q3_rayforce, benchmark_q3_pandas, benchmark_q3_native_rayforce),
        ("Q4: Group by id3, avg v1, v2, v3", benchmark_q4_rayforce, benchmark_q4_pandas, benchmark_q4_native_rayforce),
        ("Q5: Group by id3, sum v1, v2, v3", benchmark_q5_rayforce, benchmark_q5_pandas, benchmark_q5_native_rayforce),
        ("Q6: Group by id3, max(v1) - min(v2)", benchmark_q6_rayforce, benchmark_q6_pandas, benchmark_q6_native_rayforce),
    ]
    
    results = []
    
    for query_name, rayforce_py_func, pandas_func, native_rayforce_func in benchmarks:
        # Warmup
        rayforce_py_func(table)
        pandas_func(df)
        native_rayforce_func(table_name)

        rayforce_py_times = []
        pandas_times = []
        native_rayforce_times = []

        for _ in range(3):
            rf_py_time, _ = rayforce_py_func(table)
            pd_time, _ = pandas_func(df)
            native_time, _ = native_rayforce_func(table_name)
            rayforce_py_times.append(rf_py_time)
            pandas_times.append(pd_time)
            native_rayforce_times.append(native_time)

        avg_rayforce_py = sum(rayforce_py_times) / len(rayforce_py_times)
        avg_pandas = sum(pandas_times) / len(pandas_times)
        avg_native_rayforce = sum(native_rayforce_times) / len(native_rayforce_times)

        print_results(query_name, avg_rayforce_py, avg_pandas, avg_native_rayforce)
        results.append((query_name, avg_rayforce_py, avg_pandas, avg_native_rayforce))

    print("\n" + "=" * 140)
    print("SUMMARY")
    print("=" * 140)
    print(f"{'Query':<40} {'Rayforce-Py':<15} {'Pandas':<15} {'Native Rayforce':<18} {'vs Native':<12} {'vs Pandas':<12}")
    print("-" * 140)
    
    for query_name, rf_py_time, pd_time, native_time in results:
        speedup_vs_native = native_time / rf_py_time if rf_py_time > 0 else 0
        speedup_vs_pandas = pd_time / rf_py_time if rf_py_time > 0 else 0
        print(f"{query_name:<40} {rf_py_time:>12,.0f}μs {pd_time:>12,.0f}μs {native_time:>15,.0f}μs "
              f"{speedup_vs_native:>9.2f}x {speedup_vs_pandas:>9.2f}x")
    
    avg_speedup_vs_native = sum(native_time / rf_py_time for _, rf_py_time, _, native_time in results if rf_py_time > 0) / len(results)
    avg_speedup_vs_pandas = sum(pd_time / rf_py_time for _, rf_py_time, pd_time, _ in results if rf_py_time > 0) / len(results)
    print("-" * 140)
    print(f"{'Average Speedup':<40} {'':<15} {'':<15} {'':<18} {avg_speedup_vs_native:>9.2f}x {avg_speedup_vs_pandas:>9.2f}x")


if __name__ == "__main__":
    main()
