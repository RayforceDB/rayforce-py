import math

import pytest

from rayforce import types as t


@pytest.mark.parametrize(
    "value,expected",
    [
        (0, 0.0),
        (123, 123.0),
        (-123, -123.0),
        (123.45, 123.45),
        (-123.45, -123.45),
        (42.7, 42.7),
    ],
)
def test_f64(value, expected):
    assert t.F64(value).value == expected


# --- F64 special values: NaN, inf, -inf ---


def test_f64_nan():
    result = t.F64(float("nan"))
    assert math.isnan(result.value)


@pytest.mark.parametrize(
    "value,check",
    [
        (float("inf"), lambda v: math.isinf(v) and v > 0),
        (float("-inf"), lambda v: math.isinf(v) and v < 0),
    ],
)
def test_f64_infinity(value, check):
    result = t.F64(value)
    assert check(result.value)


# --- F64 precision edge cases ---


@pytest.mark.parametrize(
    "value",
    [
        5e-324,  # smallest positive subnormal
        1e-300,  # very small
        1e300,  # very large
        1.7976931348623157e308,  # near float64 max
        2.2250738585072014e-308,  # smallest positive normal
    ],
)
def test_f64_precision_extremes(value):
    assert t.F64(value).value == value
