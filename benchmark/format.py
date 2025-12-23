import sys


def intro(file=None):
    file = file or sys.stdout
    print("=" * 70, file=file)
    print("Rayforce-Py vs Pandas vs Polars vs Rayforce Benchmark", file=file)
    print("Based on H2OAI Group By Benchmark", file=file)
    print("=" * 70, file=file)


def print_results(
    query_name,
    rayforce_py_time,
    pandas_time,
    polars_time,
    native_rayforce_time,
    std_rayforce_py=0,
    std_pandas=0,
    std_polars=0,
    std_native_rayforce=0,
    polars_streaming_time=None,
    std_polars_streaming=None,
    file=None,
):
    """Print benchmark results in a formatted table."""
    file = file or sys.stdout
    print(f"\n{query_name}:", file=file)
    print(f"  Rayforce-Py:    {rayforce_py_time:,.2f} μs (±{std_rayforce_py:,.2f})", file=file)
    print(f"  Pandas:         {pandas_time:,.2f} μs (±{std_pandas:,.2f})", file=file)
    print(f"  Polars:         {polars_time:,.2f} μs (±{std_polars:,.2f})", file=file)
    if polars_streaming_time is not None:
        std_str = f" (±{std_polars_streaming:,.2f})" if std_polars_streaming else ""
        print(f"  Polars Streaming: {polars_streaming_time:,.2f} μs{std_str}", file=file)
    print(
        f"  Native Rayforce: {native_rayforce_time:,.2f} μs (±{std_native_rayforce:,.2f})",
        file=file,
    )

    if native_rayforce_time > 0:
        speedup_vs_native = native_rayforce_time / rayforce_py_time if rayforce_py_time > 0 else 0
        print(f"  Rayforce-Py vs Native: {speedup_vs_native:.2f}x", file=file)

    speedup_vs_pandas = pandas_time / rayforce_py_time if rayforce_py_time > 0 else 0
    speedup_vs_polars = polars_time / rayforce_py_time if rayforce_py_time > 0 else 0
    print(f"  Rayforce-Py vs Pandas: {speedup_vs_pandas:.2f}x", file=file)
    print(f"  Rayforce-Py vs Polars: {speedup_vs_polars:.2f}x", file=file)
    if polars_streaming_time is not None and polars_streaming_time > 0:
        speedup_vs_polars_streaming = (
            polars_streaming_time / rayforce_py_time if rayforce_py_time > 0 else 0
        )
        print(f"  Rayforce-Py vs Polars Streaming: {speedup_vs_polars_streaming:.2f}x", file=file)


def outro(file=None):
    file = file or sys.stdout
    print("\n" + "=" * 215, file=file)
    print("SUMMARY", file=file)
    print("=" * 215, file=file)
    print(
        f"{'Query':<50} {'Rayforce-Py':<15} {'Pandas':<12} {'Polars':<12} {'Polars Stream':<15} {'Native Rayforce':<18} {'vs Native':<12} {'vs Pandas':<12} {'vs Polars':<12} {'vs Polars Stream':<15}",
        file=file,
    )
    print("-" * 215, file=file)


def results(results, file=None):
    file = file or sys.stdout
    for result in results:
        if len(result) == 11:
            # New format with polars streaming
            (
                query_name,
                rf_py_time,
                pd_time,
                pl_time,
                pl_streaming_time,
                native_time,
                std_rf,
                std_pd,
                std_pl,
                std_pl_streaming,
                std_native,
            ) = result
        elif len(result) == 9:
            # Format without polars streaming
            (
                query_name,
                rf_py_time,
                pd_time,
                pl_time,
                native_time,
                std_rf,
                std_pd,
                std_pl,
                std_native,
            ) = result
            pl_streaming_time = None
        elif len(result) == 7:
            # Backward compatibility (old format without polars)
            query_name, rf_py_time, pd_time, native_time, std_rf, std_pd, std_native = result
            pl_time = 0
            pl_streaming_time = None
        else:
            # Backward compatibility (oldest format)
            query_name, rf_py_time, pd_time, native_time = result
            pl_time = 0
            pl_streaming_time = None

        speedup_vs_native = native_time / rf_py_time if rf_py_time > 0 else 0
        speedup_vs_pandas = pd_time / rf_py_time if rf_py_time > 0 else 0
        speedup_vs_polars = pl_time / rf_py_time if rf_py_time > 0 and pl_time > 0 else 0
        speedup_vs_polars_streaming = (
            pl_streaming_time / rf_py_time
            if rf_py_time > 0 and pl_streaming_time and pl_streaming_time > 0
            else 0
        )

        if pl_streaming_time is not None:
            print(
                f"{query_name:<50} {rf_py_time:>10,.0f}μs {pd_time:>10,.0f}μs {pl_time:>10,.0f}μs {pl_streaming_time:>13,.0f}μs {native_time:>15,.0f}μs "
                f"{speedup_vs_native:>9.2f}x {speedup_vs_pandas:>9.2f}x {speedup_vs_polars:>9.2f}x {speedup_vs_polars_streaming:>12.2f}x",
                file=file,
            )
        else:
            print(
                f"{query_name:<50} {rf_py_time:>10,.0f}μs {pd_time:>10,.0f}μs {pl_time:>10,.0f}μs {'':<15} {native_time:>15,.0f}μs "
                f"{speedup_vs_native:>9.2f}x {speedup_vs_pandas:>9.2f}x {speedup_vs_polars:>9.2f}x {'':<15}",
                file=file,
            )

    # Filter out Q7 from average calculations
    non_q7_results = [result for result in results if not result[0].startswith("Q7:")]

    # Calculate averages only from non-Q7 results that have valid data
    native_speedups = [
        native_time / rf_py_time
        for result in non_q7_results
        if len(result) >= 4
        and (rf_py_time := result[1]) > 0
        and (
            native_time := result[5]
            if len(result) >= 11
            else (result[4] if len(result) >= 5 else result[3])
        )
        > 0
    ]
    avg_speedup_vs_native = sum(native_speedups) / len(native_speedups) if native_speedups else 0

    pandas_speedups = [
        pd_time / rf_py_time
        for result in non_q7_results
        if len(result) >= 3 and (rf_py_time := result[1]) > 0 and (pd_time := result[2]) > 0
    ]
    avg_speedup_vs_pandas = sum(pandas_speedups) / len(pandas_speedups) if pandas_speedups else 0

    polars_results = [
        (result[3] / result[1])
        for result in non_q7_results
        if len(result) >= 4 and result[1] > 0 and result[3] > 0
    ]
    avg_speedup_vs_polars = sum(polars_results) / len(polars_results) if polars_results else 0

    polars_streaming_results = [
        (result[4] / result[1])
        for result in non_q7_results
        if len(result) >= 11 and result[1] > 0 and result[4] and result[4] > 0
    ]
    avg_speedup_vs_polars_streaming = (
        sum(polars_streaming_results) / len(polars_streaming_results)
        if polars_streaming_results
        else 0
    )

    print("-" * 215, file=file)
    print(
        f"{'Average Speedup':<50} {'':<12} {'':<12} {'':<12} {'':<15} {'':<18} {avg_speedup_vs_native:>9.2f}x {avg_speedup_vs_pandas:>9.2f}x {avg_speedup_vs_polars:>9.2f}x {avg_speedup_vs_polars_streaming:>12.2f}x",
        file=file,
    )
