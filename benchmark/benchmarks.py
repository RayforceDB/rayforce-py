from rayforce import eval_str, Column
from timer import time_microseconds
import polars as pl


class BenchmarkError(Exception): ...


class Q1:
    @staticmethod
    def benchmark_q1_rayforce(table):
        """
        Q1: Group by id1, sum v1
        """

        def run():
            return table.select(v1_sum=Column("v1").sum()).by("id1").execute()

        return time_microseconds(run)

    @staticmethod
    def benchmark_q1_pandas(df):
        """
        Q1: Group by id1, sum v1
        """

        def run():
            return df.groupby("id1")["v1"].sum().reset_index()

        return time_microseconds(run)

    @staticmethod
    def benchmark_q1_polars(df):
        """
        Q1: Group by id1, sum v1
        """

        def run():
            return df.group_by("id1").agg(pl.col("v1").sum())

        return time_microseconds(run)

    @staticmethod
    def benchmark_q1_native_rayforce(table_name):
        """
        Q1: Group by id1, sum v1
        """

        query = f"(timeit (select {{v1: (sum v1) by: id1 from: {table_name}}}))"
        result = eval_str(query)

        if isinstance(result, dict) and "time" in result:
            return result["time"] * 1000, result
        elif isinstance(result, (int, float)):
            return result * 1000, result
        elif hasattr(result, "to_python"):
            # Handle Rayforce scalar types (F64, I64, etc.)
            value = result.to_python()
            return value * 1000, result
        elif hasattr(result, "value"):
            # Handle Rayforce scalar types with value property
            value = result.value
            return value * 1000, result
        else:
            raise BenchmarkError(
                f"rayforce runtime returned unsupported measure: {type(result)}"
            )


class Q2:
    @staticmethod
    def benchmark_q2_rayforce(table):
        """
        Q2: Group by id1, id2, sum v1
        """

        def run():
            return table.select(v1_sum=Column("v1").sum()).by("id1", "id2").execute()

        return time_microseconds(run)

    @staticmethod
    def benchmark_q2_pandas(df):
        """
        Q2: Group by id1, id2, sum v1
        """

        def run():
            return df.groupby(["id1", "id2"])["v1"].sum().reset_index()

        return time_microseconds(run)

    @staticmethod
    def benchmark_q2_polars(df):
        """
        Q2: Group by id1, id2, sum v1
        """

        def run():
            return df.group_by("id1", "id2").agg(pl.col("v1").sum())

        return time_microseconds(run)

    @staticmethod
    def benchmark_q2_native_rayforce(table_name):
        """
        Q2: Group by id1, id2, sum v1
        """

        query = f"(timeit (select {{v1: (sum v1) by: {{id1: id1 id2: id2}} from: {table_name}}}))"
        result = eval_str(query)

        if isinstance(result, dict) and "time" in result:
            return result["time"] * 1000, result
        elif isinstance(result, (int, float)):
            return result * 1000, result
        elif hasattr(result, "to_python"):
            value = result.to_python()
            return value * 1000, result
        elif hasattr(result, "value"):
            value = result.value
            return value * 1000, result
        else:
            raise BenchmarkError(
                f"rayforce runtime returned unsupported measure: {type(result)}"
            )


class Q3:
    @staticmethod
    def benchmark_q3_rayforce(table):
        """
        Q3: Group by id3, sum v1, avg v3
        """

        def run():
            return (
                table.select(v1_sum=Column("v1").sum(), v3_avg=Column("v3").mean())
                .by("id3")
                .execute()
            )

        return time_microseconds(run)

    @staticmethod
    def benchmark_q3_pandas(df):
        """
        Q3: Group by id3, sum v1, avg v3
        """

        def run():
            return df.groupby("id3").agg({"v1": "sum", "v3": "mean"}).reset_index()

        return time_microseconds(run)

    @staticmethod
    def benchmark_q3_polars(df):
        """
        Q3: Group by id3, sum v1, avg v3
        """

        def run():
            return df.group_by("id3").agg(
                pl.col("v1").sum().alias("v1_sum"),
                pl.col("v3").mean().alias("v3_avg")
            )

        return time_microseconds(run)

    @staticmethod
    def benchmark_q3_native_rayforce(table_name):
        """
        Q3: Group by id3, sum v1, avg v3
        """

        query = f"(timeit (select {{v1: (sum v1) v3: (avg v3) by: id3 from: {table_name}}}))"
        result = eval_str(query)

        if isinstance(result, dict) and "time" in result:
            return result["time"] * 1000, result
        elif isinstance(result, (int, float)):
            return result * 1000, result
        elif hasattr(result, "to_python"):
            value = result.to_python()
            return value * 1000, result
        elif hasattr(result, "value"):
            value = result.value
            return value * 1000, result
        else:
            raise BenchmarkError(
                f"rayforce runtime returned unsupported measure: {type(result)}"
            )


class Q4:
    @staticmethod
    def benchmark_q4_rayforce(table):
        """
        Q4: Group by id3, avg v1, avg v2, avg v3
        """

        def run():
            return (
                table.select(
                    v1_avg=Column("v1").mean(),
                    v2_avg=Column("v2").mean(),
                    v3_avg=Column("v3").mean(),
                )
                .by("id3")
                .execute()
            )

        return time_microseconds(run)

    @staticmethod
    def benchmark_q4_pandas(df):
        """
        Q4: Group by id3, avg v1, avg v2, avg v3
        """

        def run():
            return (
                df.groupby("id3")
                .agg({"v1": "mean", "v2": "mean", "v3": "mean"})
                .reset_index()
            )

        return time_microseconds(run)

    @staticmethod
    def benchmark_q4_polars(df):
        """
        Q4: Group by id3, avg v1, avg v2, avg v3
        """

        def run():
            return df.group_by("id3").agg(
                pl.col("v1").mean().alias("v1_avg"),
                pl.col("v2").mean().alias("v2_avg"),
                pl.col("v3").mean().alias("v3_avg")
            )

        return time_microseconds(run)

    @staticmethod
    def benchmark_q4_native_rayforce(table_name):
        """
        Q4: Group by id3, avg v1, avg v2, avg v3
        """

        query = f"(timeit (select {{v1: (avg v1) v2: (avg v2) v3: (avg v3) by: id3 from: {table_name}}}))"
        result = eval_str(query)

        if isinstance(result, dict) and "time" in result:
            return result["time"] * 1000, result
        elif isinstance(result, (int, float)):
            return result * 1000, result
        elif hasattr(result, "to_python"):
            value = result.to_python()
            return value * 1000, result
        elif hasattr(result, "value"):
            value = result.value
            return value * 1000, result
        else:
            raise BenchmarkError(
                f"rayforce runtime returned unsupported measure: {type(result)}"
            )


class Q5:
    @staticmethod
    def benchmark_q5_rayforce(table):
        """
        Q5: Group by id3, sum v1, sum v2, sum v3
        """

        def run():
            return (
                table.select(
                    v1_sum=Column("v1").sum(),
                    v2_sum=Column("v2").sum(),
                    v3_sum=Column("v3").sum(),
                )
                .by("id3")
                .execute()
            )

        return time_microseconds(run)

    @staticmethod
    def benchmark_q5_pandas(df):
        """
        Q5: Group by id3, sum v1, sum v2, sum v3
        """

        def run():
            return (
                df.groupby("id3")
                .agg({"v1": "sum", "v2": "sum", "v3": "sum"})
                .reset_index()
            )

        return time_microseconds(run)

    @staticmethod
    def benchmark_q5_polars(df):
        """
        Q5: Group by id3, sum v1, sum v2, sum v3
        """

        def run():
            return df.group_by("id3").agg(
                pl.col("v1").sum().alias("v1_sum"),
                pl.col("v2").sum().alias("v2_sum"),
                pl.col("v3").sum().alias("v3_sum")
            )

        return time_microseconds(run)

    @staticmethod
    def benchmark_q5_native_rayforce(table_name):
        """
        Q5: Group by id3, sum v1, sum v2, sum v3
        """

        query = f"(timeit (select {{v1: (sum v1) v2: (sum v2) v3: (sum v3) by: id3 from: {table_name}}}))"
        result = eval_str(query)

        if isinstance(result, dict) and "time" in result:
            return result["time"] * 1000, result
        elif isinstance(result, (int, float)):
            return result * 1000, result
        elif hasattr(result, "to_python"):
            value = result.to_python()
            return value * 1000, result
        elif hasattr(result, "value"):
            value = result.value
            return value * 1000, result
        else:
            raise BenchmarkError(
                f"rayforce runtime returned unsupported measure: {type(result)}"
            )


class Q6:
    @staticmethod
    def benchmark_q6_rayforce(table):
        """
        Q6: Group by id3, max(v1) - min(v2)
        """

        def run():
            return (
                table.select(
                    range_v1_v2=(Column("v1").max() - Column("v2").min())
                )
                .by("id3")
                .execute()
            )

        return time_microseconds(run)

    @staticmethod
    def benchmark_q6_pandas(df):
        """
        Q6: Group by id3, max(v1) - min(v2)
        """

        def run():
            grouped = df.groupby("id3").agg({"v1": "max", "v2": "min"})
            grouped["range_v1_v2"] = grouped["v1"] - grouped["v2"]
            return grouped[["range_v1_v2"]].reset_index()

        return time_microseconds(run)

    @staticmethod
    def benchmark_q6_polars(df):
        """
        Q6: Group by id3, max(v1) - min(v2)
        """

        def run():
            return df.group_by("id3").agg(
                (pl.col("v1").max() - pl.col("v2").min()).alias("range_v1_v2")
            )

        return time_microseconds(run)

    @staticmethod
    def benchmark_q6_native_rayforce(table_name):
        """
        Q6: Group by id3, max(v1) - min(v2)
        """

        query = f"(timeit (select {{range_v1_v2: (- (max v1) (min v2)) by: id3 from: {table_name}}}))"
        result = eval_str(query)

        if isinstance(result, dict) and "time" in result:
            return result["time"] * 1000, result
        elif isinstance(result, (int, float)):
            return result * 1000, result
        elif hasattr(result, "to_python"):
            value = result.to_python()
            return value * 1000, result
        elif hasattr(result, "value"):
            value = result.value
            return value * 1000, result
        else:
            raise BenchmarkError(
                f"rayforce runtime returned unsupported measure: {type(result)}"
            )


benchmarks = [
    (
        "Q1: Group by id1, sum v1",
        Q1.benchmark_q1_rayforce,
        Q1.benchmark_q1_pandas,
        Q1.benchmark_q1_polars,
        Q1.benchmark_q1_native_rayforce,
    ),
    (
        "Q2: Group by id1, id2, sum v1",
        Q2.benchmark_q2_rayforce,
        Q2.benchmark_q2_pandas,
        Q2.benchmark_q2_polars,
        Q2.benchmark_q2_native_rayforce,
    ),
    (
        "Q3: Group by id3, sum v1, avg v3",
        Q3.benchmark_q3_rayforce,
        Q3.benchmark_q3_pandas,
        Q3.benchmark_q3_polars,
        Q3.benchmark_q3_native_rayforce,
    ),
    (
        "Q4: Group by id3, avg v1, v2, v3",
        Q4.benchmark_q4_rayforce,
        Q4.benchmark_q4_pandas,
        Q4.benchmark_q4_polars,
        Q4.benchmark_q4_native_rayforce,
    ),
    (
        "Q5: Group by id3, sum v1, v2, v3",
        Q5.benchmark_q5_rayforce,
        Q5.benchmark_q5_pandas,
        Q5.benchmark_q5_polars,
        Q5.benchmark_q5_native_rayforce,
    ),
    (
        "Q6: Group by id3, max(v1) - min(v2)",
        Q6.benchmark_q6_rayforce,
        Q6.benchmark_q6_pandas,
        Q6.benchmark_q6_polars,
        Q6.benchmark_q6_native_rayforce,
    ),
]
