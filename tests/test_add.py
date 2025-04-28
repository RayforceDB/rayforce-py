import pytest

from raypy import i64, f64, add


class TestAddFloat:
    @pytest.mark.parametrize(
        "x, y, expected",
        [
            (5.5, 3.1, 8.6),
            (10.5, 2, 12.5),
            (-7.2, 4.5, -2.7),
            (f64(3.14), 2.86, 6.0),
            (f64(1.5), f64(2.5), 4.0),
            (f64(5.5), 10, 15.5),
            (5, 3, 8),
            (1000, 42, 1042),
            (-5, 10, 5),
            (i64(10), 5, 15),
            (i64(20), i64(30), 50),
        ],
    )
    def test_scalar_adding(self, x, y, expected):
        result = add(x, y)
        assert result == expected, f"Expected {expected}, got {result}"

    @pytest.mark.parametrize(
        "x, y, expected",
        [
            ([1, 2, 3], 3, [4, 5, 6]),
            ([1, 2, 3], 3.1, [4.1, 5.1, 6.1]),
            (3.1, [1, 2, 3], [4.1, 5.1, 6.1]),
            ([1, 2, 3], [4, 5, 6], [5, 7, 9]),
            ([1, 2, 3], [4.5, 5.5, 6.5], [5.5, 7.5, 9.5]),
        ],
    )
    def test_list_adding(self, x, y, expected):
        result = add(x, y)
        assert result == expected, f"Expected {expected}, got {result}"
