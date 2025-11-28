from rayforce import _rayforce_c as r
from rayforce.types.operators import Operation


def test_all_operations_have_primitives():
    for op in Operation:
        primitive = op.primitive

        assert isinstance(primitive, r.RayObject), (
            f"Operation {op.name} ({op.value}) has no primitive"
        )

        assert primitive.get_obj_type() in (
            r.TYPE_UNARY,
            r.TYPE_BINARY,
            r.TYPE_VARY,
        ), f"Operation {op.name} ({op.value}) primitive has invalid type: {
            primitive.get_obj_type()
        }"


def test_operation_properties():
    add_op = Operation.ADD
    assert add_op.is_binary or add_op.is_unary or add_op.is_variadic

    negate_op = Operation.NEGATE
    assert negate_op.is_binary or negate_op.is_unary or add_op.is_variadic

    for op in Operation:
        assert op.is_binary or op.is_unary or op.is_variadic, (
            f"Operation {op.name} ({op.value}) is not binary, unary, or variadic"
        )
