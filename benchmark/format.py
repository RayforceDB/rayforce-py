def intro():
    print("=" * 70)
    print("Rayforce-Py vs Pandas vs Polars vs DuckDB vs Rayforce Benchmark")
    print("Based on H2OAI Group By Benchmark")
    print("=" * 70)


def print_results(
    query_name,
    rayforce_py_time,
    pandas_time,
    polars_time,
    duckdb_time,
    native_rayforce_time,
    std_rayforce_py=0,
    std_pandas=0,
    std_polars=0,
    std_duckdb=0,
    std_native_rayforce=0,
):
    """Print benchmark results in a formatted table."""
    print(f"\n{query_name}:")
    print(f"  Rayforce-Py:     {rayforce_py_time:,.2f} μs (±{std_rayforce_py:,.2f})")
    print(f"  Pandas:          {pandas_time:,.2f} μs (±{std_pandas:,.2f})")
    print(f"  Polars:          {polars_time:,.2f} μs (±{std_polars:,.2f})")
    print(f"  DuckDB:          {duckdb_time:,.2f} μs (±{std_duckdb:,.2f})")
    print(f"  Native Rayforce: {native_rayforce_time:,.2f} μs (±{std_native_rayforce:,.2f})")

    if native_rayforce_time > 0:
        speedup_vs_native = native_rayforce_time / rayforce_py_time if rayforce_py_time > 0 else 0
        print(f"  Rayforce-Py vs Native: {speedup_vs_native:.2f}x")

    speedup_vs_pandas = pandas_time / rayforce_py_time if rayforce_py_time > 0 else 0
    speedup_vs_polars = polars_time / rayforce_py_time if rayforce_py_time > 0 else 0
    speedup_vs_duckdb = duckdb_time / rayforce_py_time if rayforce_py_time > 0 else 0
    print(f"  Rayforce-Py vs Pandas: {speedup_vs_pandas:.2f}x")
    print(f"  Rayforce-Py vs Polars: {speedup_vs_polars:.2f}x")
    print(f"  Rayforce-Py vs DuckDB: {speedup_vs_duckdb:.2f}x")


def outro():
    print("\n" + "=" * 210)
    print("SUMMARY")
    print("=" * 210)
    print(
        f"{'Query':<40} {'Rayforce-Py':>12} {'Pandas':>12} {'Polars':>12} {'DuckDB':>12} {'Native Rayforce':>18} {'vs Native':>12} {'vs Pandas':>12} {'vs Polars':>12} {'vs DuckDB':>12}"
    )
    print("-" * 210)


def results(results):
    for result in results:
        if len(result) == 11:
            (
                query_name,
                rf_py_time,
                pd_time,
                pl_time,
                duck_time,
                native_time,
                _,
                _,
                _,
                _,
                _,
            ) = result
        elif len(result) == 9:
            # Backward compatibility (format without duckdb)
            (
                query_name,
                rf_py_time,
                pd_time,
                pl_time,
                native_time,
                _,
                _,
                _,
                _,
            ) = result
            duck_time = 0
        else:
            # Backward compatibility (oldest format)
            query_name, rf_py_time, pd_time, native_time = result[:4]
            pl_time = 0
            duck_time = 0

        speedup_vs_native = native_time / rf_py_time if rf_py_time > 0 else 0
        speedup_vs_pandas = pd_time / rf_py_time if rf_py_time > 0 else 0
        speedup_vs_polars = pl_time / rf_py_time if rf_py_time > 0 and pl_time > 0 else 0
        speedup_vs_duckdb = duck_time / rf_py_time if rf_py_time > 0 and duck_time > 0 else 0
        print(
            f"{query_name:<40} {rf_py_time:>12,.0f}μs {pd_time:>12,.0f}μs {pl_time:>12,.0f}μs {duck_time:>12,.0f}μs {native_time:>15,.0f}μs "
            f"{speedup_vs_native:>9.2f}x {speedup_vs_pandas:>9.2f}x {speedup_vs_polars:>9.2f}x {speedup_vs_duckdb:>9.2f}x"
        )

    # Calculate averages
    avg_speedup_vs_native = (
        sum(
            result[5] / result[1]
            if len(result) >= 11
            else result[4] / result[1]
            if len(result) >= 9
            else result[3] / result[1]
            for result in results
            if result[1] > 0
        )
        / len(results)
        if results
        else 0
    )

    avg_speedup_vs_pandas = (
        sum(result[2] / result[1] for result in results if result[1] > 0 and result[2] > 0)
        / len(results)
        if results
        else 0
    )

    avg_speedup_vs_polars = (
        sum(result[3] / result[1] for result in results if result[1] > 0 and result[3] > 0)
        / len(results)
        if results
        else 0
    )

    avg_speedup_vs_duckdb = (
        sum(
            result[4] / result[1]
            for result in results
            if len(result) >= 11 and result[1] > 0 and result[4] > 0
        )
        / len([r for r in results if len(r) >= 11 and r[4] > 0])
        if any(len(r) >= 11 and r[4] > 0 for r in results)
        else 0
    )

    print("-" * 210)
    print(
        f"{'Average Speedup':<40} {'':<12} {'':<12} {'':<12} {'':<12} {'':<18} {avg_speedup_vs_native:>9.2f}x {avg_speedup_vs_pandas:>9.2f}x {avg_speedup_vs_polars:>9.2f}x {avg_speedup_vs_duckdb:>9.2f}x"
    )
