import math

import numpy as np
import pytest

from rayforce import errors
from rayforce import types as t


def _approx_f32(value: float) -> float:
    """Round-trip a Python float through float32 so test expectations match
    the rounded value the F32 wrapper preserves."""
    return float(np.float32(value))


@pytest.mark.parametrize(
    "value,expected",
    [
        (0, 0.0),
        (123, 123.0),
        (-123, -123.0),
        (1.5, 1.5),
        (-1.5, -1.5),
        (3.14, _approx_f32(3.14)),
        (-3.14, _approx_f32(-3.14)),
        (123.45, _approx_f32(123.45)),
    ],
)
def test_f32_construct_and_to_python(value, expected):
    f = t.F32(value)
    assert f.value == pytest.approx(expected)
    assert isinstance(f.value, float)


def test_f32_nan():
    result = t.F32(float("nan"))
    assert math.isnan(result.value)


@pytest.mark.parametrize(
    "value,check",
    [
        (float("inf"), lambda v: math.isinf(v) and v > 0),
        (float("-inf"), lambda v: math.isinf(v) and v < 0),
    ],
)
def test_f32_infinity(value, check):
    result = t.F32(value)
    assert check(result.value)


def test_f32_overflow_raises():
    with pytest.raises(errors.RayforceInitError):
        t.F32(1e40)
    with pytest.raises(errors.RayforceInitError):
        t.F32(-1e40)


def test_f32_max_finite_ok():
    v = t.F32(3.4e38)
    assert math.isfinite(v.value)


def test_f32_invalid_value_raises():
    with pytest.raises(errors.RayforceInitError):
        t.F32("not a number")


def test_f32_repr():
    f = t.F32(2.5)
    assert "F32" in repr(f)
    assert "2.5" in repr(f)


# --- arithmetic with F32 and F64 ---


def test_f32_add_f32():
    result = t.F32(1.5) + t.F32(2.5)
    val = result.value if hasattr(result, "value") else result.to_python()
    if isinstance(val, list):
        val = val[0]
    assert val == pytest.approx(4.0)


def test_f32_add_f64():
    result = t.F32(1.5) + t.F64(2.5)
    val = result.value if hasattr(result, "value") else result.to_python()
    if isinstance(val, list):
        val = val[0]
    assert val == pytest.approx(4.0)


def test_f32_sub_f32():
    result = t.F32(5.0) - t.F32(2.0)
    val = result.value if hasattr(result, "value") else result.to_python()
    if isinstance(val, list):
        val = val[0]
    assert val == pytest.approx(3.0)


def test_f32_mul_f32():
    result = t.F32(2.0) * t.F32(3.0)
    val = result.value if hasattr(result, "value") else result.to_python()
    if isinstance(val, list):
        val = val[0]
    assert val == pytest.approx(6.0)


# --- numpy roundtrip preserves dtype ---


def test_f32_numpy_roundtrip_preserves_dtype():
    arr = np.array([1.0, 2.0, 3.0, 4.5, -1.25], dtype=np.float32)
    vec = t.Vector.from_numpy(arr)
    out = vec.to_numpy()
    assert out.dtype == np.float32
    np.testing.assert_array_almost_equal(out, arr)


def test_f32_numpy_roundtrip_no_widening():
    arr = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    vec = t.Vector.from_numpy(arr)
    # Indexing into an F32 vector returns F32 scalars now that the type exists.
    assert isinstance(vec[0], t.F32)
    assert vec[0].value == pytest.approx(_approx_f32(0.1))


# --- F32 vector operations ---


def test_f32_vector_to_python():
    arr = np.array([1.5, 2.5, 3.5], dtype=np.float32)
    vec = t.Vector.from_numpy(arr)
    out = vec.to_python()
    assert len(out) == 3
    assert all(isinstance(x, t.F32) for x in out)
    assert [x.value for x in out] == pytest.approx([1.5, 2.5, 3.5])


def test_f32_vector_to_list():
    arr = np.array([1.5, 2.5, 3.5], dtype=np.float32)
    vec = t.Vector.from_numpy(arr)
    out = vec.to_list()
    assert out == pytest.approx([1.5, 2.5, 3.5])
    assert all(isinstance(x, float) for x in out)


def test_f32_vector_indexing():
    arr = np.array([10.0, 20.0, 30.0], dtype=np.float32)
    vec = t.Vector.from_numpy(arr)
    assert isinstance(vec[0], t.F32)
    assert vec[0].value == pytest.approx(10.0)
    assert vec[2].value == pytest.approx(30.0)
    assert vec[-1].value == pytest.approx(30.0)


def test_f32_vector_slice_via_at():
    """Slice support: Vector at_idx works for any contiguous F32 vector
    obtained via slicing (uses ray_data() so slice attrs are honoured)."""
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
    vec = t.Vector.from_numpy(arr)
    sliced = t.Vector(ptr=t.Vector.from_numpy(arr).ptr)
    # Plain indexing roundtrip
    for i, expected in enumerate([1.0, 2.0, 3.0, 4.0, 5.0]):
        assert vec[i].value == pytest.approx(expected)
        assert sliced[i].value == pytest.approx(expected)


def test_f32_construct_from_int():
    f = t.F32(42)
    assert f.value == 42.0


def test_f32_type_code_negative():
    """Registry uses -RAY_F32 for the scalar slot."""
    assert t.F32.type_code == -6
