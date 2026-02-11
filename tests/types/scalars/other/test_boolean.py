import pytest

from rayforce import types as t
from rayforce.errors import RayforceInitError


@pytest.mark.parametrize(
    "value,expected",
    [
        (True, True),
        (False, False),
        (0, False),
        (1, True),
        ("True", True),
        ("False", True),  # non-empty strings are truthy
    ],
)
def test_b8(value, expected):
    assert t.B8(value).value == expected


# --- B8: truthy/falsy edge cases ---


@pytest.mark.parametrize(
    "value,expected",
    [
        (0.0, False),  # float zero is falsy
        ("", False),  # empty string is falsy
        ([], False),  # empty list is falsy
        (2, True),  # non-zero int is truthy
        (-1, True),  # negative int is truthy
    ],
)
def test_b8_truthy_falsy_edge_cases(value, expected):
    assert t.B8(value).value == expected


def test_b8_none_raises():
    """None is not a valid value; it triggers the 'no value or ptr' error."""
    with pytest.raises(RayforceInitError):
        t.B8(None)
