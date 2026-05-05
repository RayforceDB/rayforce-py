"""Comprehensive tests for rayforce.utils.evaluation (eval_str, eval_obj)."""

from __future__ import annotations

import pytest

from rayforce import I64, List, Operation, Vector, errors, eval_obj, eval_str

# ── eval_str: arithmetic ─────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("(+ 1 2)", 3),
        ("(- 5 3)", 2),
        ("(* 4 5)", 20),
        ("(+ -5 10)", 5),
        ("(* 0 100)", 0),
        ("(+ 0 0)", 0),
        ("(- 0 -1)", 1),
        ("(+ 100 200)", 300),
        ("(- 1000 500)", 500),
        ("(* -3 4)", -12),
    ],
)
def test_eval_str_integer_arithmetic(expr, expected):
    assert eval_str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("(+ 1.5 2.5)", 4.0),
        ("(- 5.5 1.5)", 4.0),
        ("(* 2.5 4)", 10.0),
        ("(/ 10.0 4.0)", 2.5),
        ("(/ 1.0 4.0)", 0.25),
        ("(/ 100.0 25.0)", 4.0),
    ],
)
def test_eval_str_float_arithmetic(expr, expected):
    assert eval_str(expr) == pytest.approx(expected)


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("(/ 10 4)", 2.5),
        ("(/ 1 4)", 0.25),
        ("(/ 10 5)", 2.0),
        ("(/ 100 10)", 10.0),
    ],
)
def test_eval_str_int_division_returns_float(expr, expected):
    """v2 `/` is true division — returns F64 even on integer operands."""
    result = eval_str(expr)
    assert result == pytest.approx(expected)


@pytest.mark.parametrize(
    "expr, expected", [("(div 10 4)", 2), ("(div 10 3)", 3), ("(div 100 30)", 3)]
)
def test_eval_str_int_floor_division(expr, expected):
    assert eval_str(expr) == expected


# ── eval_str: comparison ────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("(< 1 2)", True),
        ("(< 2 1)", False),
        ("(> 5 3)", True),
        ("(> 1 1)", False),
        ("(<= 1 1)", True),
        ("(<= 1 0)", False),
        ("(>= 1 1)", True),
        ("(>= 0 1)", False),
        ("(== 1 1)", True),
        ("(== 1 2)", False),
        ("(!= 1 2)", True),
        ("(!= 5 5)", False),
    ],
)
def test_eval_str_comparison(expr, expected):
    assert eval_str(expr) == expected


# ── eval_str: vectors and aggregations ──────────────────────────────────────


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("(sum (til 5))", 10),
        ("(sum (til 10))", 45),
        ("(sum (til 100))", 4950),
        ("(sum [1 2 3 4 5])", 15),
        ("(sum [10 20 30])", 60),
    ],
)
def test_eval_str_sum(expr, expected):
    assert eval_str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected", [("(min [3 1 4 1 5 9 2 6])", 1), ("(max [3 1 4 1 5 9 2 6])", 9)]
)
def test_eval_str_min_max(expr, expected):
    assert eval_str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [("(first [10 20 30])", 10), ("(last [10 20 30])", 30), ("(count [10 20 30 40])", 4)],
)
def test_eval_str_element_access(expr, expected):
    assert eval_str(expr) == expected


# ── eval_str: til ────────────────────────────────────────────────────────────


@pytest.mark.parametrize("n", [0, 1, 5, 10, 100])
def test_eval_str_til(n):
    result = eval_str(f"(til {n})")
    assert [v.value for v in result] == list(range(n))


# ── eval_str: errors ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "expr",
    [
        "(undefined_function 1 2)",
        "(",  # parse error
        ")",  # parse error
        "(.bogus.namespace.fn 1)",
    ],
)
def test_eval_str_errors(expr):
    with pytest.raises(errors.RayforceError):
        eval_str(expr)


def test_eval_str_divide_by_zero_returns_zero():
    """v2 (/ x 0) returns 0.0 (no exception)."""
    assert eval_str("(/ 1 0)") == 0.0
    assert eval_str("(/ 100 0)") == 0.0


@pytest.mark.parametrize("invalid", [123, 1.5, [], None, object()])
def test_eval_str_requires_string(invalid):
    with pytest.raises(errors.RayforceEvaluationError):
        eval_str(invalid)


# ── eval_str: raw mode ──────────────────────────────────────────────────────


def test_eval_str_raw_returns_ray_object():
    from rayforce import _rayforce_c as r

    result = eval_str("(+ 1 2)", raw=True)
    assert isinstance(result, r.RayObject)


def test_eval_str_default_returns_python_scalar():
    """eval_str default boxes scalars as rayforce types (e.g. I64)."""

    result = eval_str("(+ 1 2)")
    # I64 wraps an int; comparison via .value works either way.
    assert result == 3


# ── eval_obj: ────────────────────────────────────────────────────────────────


def test_eval_obj_with_list():
    vec = Vector([1, 2, 3, 4, 5], ray_type=I64)
    result = eval_obj(List([Operation.SUM, vec]))
    assert result == 15


def test_eval_obj_with_arith():
    result = eval_obj(List([Operation.ADD, I64(5), I64(7)]))
    assert result == 12


@pytest.mark.parametrize(
    "op, args, expected",
    [
        (Operation.ADD, (I64(2), I64(3)), 5),
        (Operation.SUBTRACT, (I64(10), I64(4)), 6),
        (Operation.MULTIPLY, (I64(3), I64(7)), 21),
        (Operation.MODULO, (I64(10), I64(3)), 1),
    ],
)
def test_eval_obj_binary_ops(op, args, expected):
    result = eval_obj(List([op, *args]))
    assert result == expected


def test_eval_obj_invalid_input_raises():
    with pytest.raises(errors.RayforceEvaluationError):
        eval_obj(123)


def test_eval_obj_with_vector_arg():
    vec = Vector([10, 20, 30, 40, 50], ray_type=I64)
    result = eval_obj(List([Operation.SUM, vec]))
    assert result == 150
