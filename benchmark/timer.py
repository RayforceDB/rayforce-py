import time


def time_microseconds(func, *args, **kwargs):
    """
    Measure function execution time in microseconds.
    """

    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    return (end - start) * 1_000_000, result
