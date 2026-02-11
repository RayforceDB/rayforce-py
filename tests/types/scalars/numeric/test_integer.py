import pytest

from rayforce import types as t


@pytest.mark.parametrize("value,expected", [(0, 0), (100, 100), (-100, -100)])
def test_i16(value, expected):
    assert t.I16(value).value == expected


@pytest.mark.parametrize("value,expected", [(0, 0), (1000, 1000), (-1000, -1000)])
def test_i32(value, expected):
    assert t.I32(value).value == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (0, 0),
        (1_000_000, 1_000_000),
        (-1_000_000, -1_000_000),
        (42, 42),
        (2_147_483_647, 2_147_483_647),
        (-2_147_483_648, -2_147_483_648),
    ],
)
def test_i64(value, expected):
    assert t.I64(value).value == expected


# --- I16 boundary values ---


@pytest.mark.parametrize(
    "value,expected",
    [
        (-32768, -32768),  # I16 MIN
        (32767, 32767),  # I16 MAX
    ],
)
def test_i16_boundary_values(value, expected):
    assert t.I16(value).value == expected


# --- I32 boundary values ---


@pytest.mark.parametrize(
    "value,expected",
    [
        (-2_147_483_648, -2_147_483_648),  # I32 MIN
        (2_147_483_647, 2_147_483_647),  # I32 MAX
    ],
)
def test_i32_boundary_values(value, expected):
    assert t.I32(value).value == expected


# --- I64 boundary values ---


@pytest.mark.parametrize(
    "value,expected",
    [
        (-9_223_372_036_854_775_808, -9_223_372_036_854_775_808),  # I64 MIN
        (9_223_372_036_854_775_807, 9_223_372_036_854_775_807),  # I64 MAX
    ],
)
def test_i64_boundary_values(value, expected):
    assert t.I64(value).value == expected


# --- I16/I32 overflow: C library wraps around silently ---


@pytest.mark.parametrize(
    "value,expected",
    [
        (32768, -32768),  # MAX+1 wraps to MIN
        (-32769, 32767),  # MIN-1 wraps to MAX
    ],
)
def test_i16_overflow_wraps(value, expected):
    assert t.I16(value).value == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (2_147_483_648, -2_147_483_648),  # MAX+1 wraps to MIN
        (-2_147_483_649, 2_147_483_647),  # MIN-1 wraps to MAX
    ],
)
def test_i32_overflow_wraps(value, expected):
    assert t.I32(value).value == expected


# --- I64 overflow: C library raises RuntimeError for values beyond 64-bit ---


@pytest.mark.parametrize(
    "value",
    [
        9_223_372_036_854_775_808,  # MAX+1
        -9_223_372_036_854_775_809,  # MIN-1
    ],
)
def test_i64_overflow_raises(value):
    with pytest.raises(RuntimeError):
        t.I64(value)
