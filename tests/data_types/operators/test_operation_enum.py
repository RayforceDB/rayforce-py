import pytest

from rayforce import F64, FFI, I64, List, Vector, eval_obj
from rayforce import _rayforce_c as r
from rayforce.types.operators import Operation


def test_all_operations_have_primitives():
    for op in Operation:
        primitive = op.primitive

        assert isinstance(primitive, r.RayObject), (
            f"Operation {op.name} ({op.value}) has no primitive"
        )

        assert FFI.get_obj_type(primitive) in (
            r.TYPE_UNARY,
            r.TYPE_BINARY,
            r.TYPE_VARY,
        ), (
            f"Operation {op.name} ({op.value}) primitive has invalid type: {FFI.get_obj_type(primitive)}"
        )


def test_operation_properties():
    add_op = Operation.ADD
    assert add_op.is_binary or add_op.is_unary or add_op.is_variadic

    negate_op = Operation.NEGATE
    assert negate_op.is_binary or negate_op.is_unary or negate_op.is_variadic

    for op in Operation:
        assert op.is_binary or op.is_unary or op.is_variadic, (
            f"Operation {op.name} ({op.value}) is not binary, unary, or variadic"
        )


# ---------------------------------------------------------------------------
# Individual operation execution tests
# ---------------------------------------------------------------------------


def test_operation_add_scalars():
    result = eval_obj(List([Operation.ADD, I64(3), I64(7)]))
    assert result.value == 10


def test_operation_subtract_scalars():
    result = eval_obj(List([Operation.SUBTRACT, I64(10), I64(4)]))
    assert result.value == 6


def test_operation_multiply_scalars():
    result = eval_obj(List([Operation.MULTIPLY, I64(5), I64(6)]))
    assert result.value == 30


def test_operation_divide_scalars():
    result = eval_obj(List([Operation.DIVIDE, F64(10.0), F64(4.0)]))
    assert abs(result.value - 2.5) < 1e-9


def test_operation_modulo_scalars():
    result = eval_obj(List([Operation.MODULO, I64(10), I64(3)]))
    assert result.value == 1


def test_operation_negate_vector():
    vec = Vector([3, 1, 2], ray_type=I64)
    result = eval_obj(List([Operation.NEGATE, vec]))
    assert result[0].value == -3
    assert result[1].value == -1
    assert result[2].value == -2


def test_operation_equals():
    result = eval_obj(List([Operation.EQUALS, I64(5), I64(5)]))
    assert result.value is True


def test_operation_not_equals():
    result = eval_obj(List([Operation.NOT_EQUALS, I64(5), I64(3)]))
    assert result.value is True


def test_operation_greater_than():
    result = eval_obj(List([Operation.GREATER_THAN, I64(5), I64(3)]))
    assert result.value is True


def test_operation_less_than():
    result = eval_obj(List([Operation.LESS_THAN, I64(3), I64(5)]))
    assert result.value is True


def test_operation_greater_equal():
    result = eval_obj(List([Operation.GREATER_EQUAL, I64(5), I64(5)]))
    assert result.value is True


def test_operation_less_equal():
    result = eval_obj(List([Operation.LESS_EQUAL, I64(5), I64(5)]))
    assert result.value is True


def test_operation_and():
    from rayforce import B8

    result = eval_obj(List([Operation.AND, B8(True), B8(False)]))
    assert result.value is False


def test_operation_or():
    from rayforce import B8

    result = eval_obj(List([Operation.OR, B8(True), B8(False)]))
    assert result.value is True


def test_operation_not():
    from rayforce import B8

    result = eval_obj(List([Operation.NOT, B8(True)]))
    assert result.value is False


def test_operation_sum_vector():
    vec = Vector([1, 2, 3, 4, 5], ray_type=I64)
    result = eval_obj(List([Operation.SUM, vec]))
    assert result.value == 15


def test_operation_avg_vector():
    vec = Vector([10.0, 20.0, 30.0], ray_type=F64)
    result = eval_obj(List([Operation.AVG, vec]))
    assert abs(result.value - 20.0) < 1e-9


def test_operation_min_vector():
    vec = Vector([5, 1, 8, 3], ray_type=I64)
    result = eval_obj(List([Operation.MIN, vec]))
    assert result.value == 1


def test_operation_max_vector():
    vec = Vector([5, 1, 8, 3], ray_type=I64)
    result = eval_obj(List([Operation.MAX, vec]))
    assert result.value == 8


def test_operation_count_vector():
    vec = Vector([10, 20, 30], ray_type=I64)
    result = eval_obj(List([Operation.COUNT, vec]))
    assert result.value == 3


def test_operation_first_vector():
    vec = Vector([10, 20, 30], ray_type=I64)
    result = eval_obj(List([Operation.FIRST, vec]))
    assert result.value == 10


def test_operation_last_vector():
    vec = Vector([10, 20, 30], ray_type=I64)
    result = eval_obj(List([Operation.LAST, vec]))
    assert result.value == 30


def test_operation_reverse_vector():
    vec = Vector([1, 2, 3], ray_type=I64)
    result = eval_obj(List([Operation.REVERSE, vec]))
    assert [result[i].value for i in range(len(result))] == [3, 2, 1]


def test_operation_distinct_vector():
    vec = Vector([1, 2, 2, 3, 3, 3], ray_type=I64)
    result = eval_obj(List([Operation.DISTINCT, vec]))
    values = [result[i].value for i in range(len(result))]
    assert sorted(values) == [1, 2, 3]


def test_operation_asc_vector():
    vec = Vector([3, 1, 2], ray_type=I64)
    result = eval_obj(List([Operation.ASC, vec]))
    values = [result[i].value for i in range(len(result))]
    assert values == [1, 2, 3]


def test_operation_desc_vector():
    vec = Vector([3, 1, 2], ray_type=I64)
    result = eval_obj(List([Operation.DESC, vec]))
    values = [result[i].value for i in range(len(result))]
    assert values == [3, 2, 1]


def test_operation_add_vectors():
    v1 = Vector([1, 2, 3], ray_type=I64)
    v2 = Vector([10, 20, 30], ray_type=I64)
    result = eval_obj(List([Operation.ADD, v1, v2]))
    values = [result[i].value for i in range(len(result))]
    assert values == [11, 22, 33]


def test_operation_from_ptr_roundtrip():
    """Verify Operation.from_ptr can reconstruct the operation from its primitive."""
    for op in [Operation.ADD, Operation.SUM, Operation.NOT]:
        reconstructed = Operation.from_ptr(op.primitive)
        assert reconstructed == op


def test_operation_from_ptr_covers_all_operations():
    """Every Operation must be reconstructible from its own primitive pointer."""
    for op in Operation:
        assert Operation.from_ptr(op.primitive) == op


def test_operation_from_ptr_rejects_non_operation():
    """from_ptr must reject objects that aren't UNARY/BINARY/VARY."""
    from rayforce.errors import RayforceInitError

    with pytest.raises(RayforceInitError, match="not an operation"):
        Operation.from_ptr(I64(42).ptr)


def test_operation_til():
    result = eval_obj(List([Operation.TIL, I64(5)]))
    values = [result[i].value for i in range(len(result))]
    assert values == [0, 1, 2, 3, 4]


def test_operation_enlist():
    result = eval_obj(List([Operation.ENLIST, I64(42)]))
    assert len(result) == 1
    assert result[0].value == 42
