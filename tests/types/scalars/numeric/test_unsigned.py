import pytest

from rayforce import types as t


@pytest.mark.parametrize(
    "value,expected",
    [
        (0, 0),
        (100, 100),
        (255, 255),
        (42.7, 42),
    ],
)
def test_u8(value, expected):
    assert t.U8(value).value == expected


# --- U8 negative input: C library wraps around (unsigned underflow) ---


@pytest.mark.parametrize(
    "value,expected",
    [
        (-1, 255),  # wraps to 255
        (-128, 128),
    ],
)
def test_u8_negative_wraps(value, expected):
    assert t.U8(value).value == expected


# --- U8 overflow (256+): C library wraps around modulo 256 ---


@pytest.mark.parametrize(
    "value,expected",
    [
        (256, 0),  # wraps to 0
        (257, 1),
        (1000, 232),  # 1000 % 256 = 232
    ],
)
def test_u8_overflow_wraps(value, expected):
    assert t.U8(value).value == expected


# --- U8 extreme values beyond C int range raise RuntimeError ---


@pytest.mark.parametrize(
    "value",
    [
        2**64,
        -(2**64),
    ],
)
def test_u8_extreme_overflow_raises(value):
    with pytest.raises(RuntimeError):
        t.U8(value)
