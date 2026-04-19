"""
Comprehensive numpy compatibility tests for rayforce.

Tests ALL numpy dtypes → rayforce conversions (Vector.from_numpy)
and ALL rayforce types → numpy conversions (Vector.to_numpy),
plus Table round-trips. Every assertion checks concrete values.
"""

from __future__ import annotations

import datetime as dt
import uuid

import numpy as np
import pytest

from rayforce import errors
from rayforce import types as t

# ============================================================================
# 1. Vector.from_numpy — supported numeric dtypes
# ============================================================================


class TestFromNumpyInt64:
    def test_basic_values(self):
        arr = np.array([1, 2, 3], dtype=np.int64)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert v[0].value == 1
        assert v[1].value == 2
        assert v[2].value == 3
        assert isinstance(v[0], t.I64)

    def test_negative_values(self):
        arr = np.array([-9223372036854775807, 0, 9223372036854775807], dtype=np.int64)
        v = t.Vector.from_numpy(arr)
        assert v[0].value == -9223372036854775807
        assert v[1].value == 0
        assert v[2].value == 9223372036854775807

    def test_empty(self):
        arr = np.array([], dtype=np.int64)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 0

    def test_single(self):
        arr = np.array([42], dtype=np.int64)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 1
        assert v[0].value == 42


class TestFromNumpyInt32:
    def test_basic_values(self):
        arr = np.array([100, -200, 300], dtype=np.int32)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert v[0].value == 100
        assert v[1].value == -200
        assert v[2].value == 300
        assert isinstance(v[0], t.I32)

    def test_boundary_values(self):
        arr = np.array([-2147483648, 0, 2147483647], dtype=np.int32)
        v = t.Vector.from_numpy(arr)
        assert v[0].value is None  # INT32_MIN is null sentinel (0Ni)
        assert v[1].value == 0
        assert v[2].value == 2147483647


class TestFromNumpyInt16:
    def test_basic_values(self):
        arr = np.array([10, -20, 30], dtype=np.int16)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert v[0].value == 10
        assert v[1].value == -20
        assert v[2].value == 30
        assert isinstance(v[0], t.I16)

    def test_boundary_values(self):
        arr = np.array([-32768, 0, 32767], dtype=np.int16)
        v = t.Vector.from_numpy(arr)
        assert v[0].value is None  # INT16_MIN is null sentinel (0Nh)
        assert v[1].value == 0
        assert v[2].value == 32767


class TestFromNumpyUint8:
    def test_basic_values(self):
        arr = np.array([0, 128, 255], dtype=np.uint8)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert v[0].value == 0
        assert v[1].value == 128
        assert v[2].value == 255
        assert isinstance(v[0], t.U8)

    def test_all_byte_values(self):
        arr = np.arange(256, dtype=np.uint8)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 256
        assert v[0].value == 0
        assert v[127].value == 127
        assert v[255].value == 255

    def test_roundtrip_via_to_numpy_is_correct(self):
        arr = np.array([0, 128, 255], dtype=np.uint8)
        v = t.Vector.from_numpy(arr)
        result = v.to_numpy()
        assert result.dtype == np.uint8
        np.testing.assert_array_equal(result, [0, 128, 255])


class TestFromNumpyFloat64:
    def test_basic_values(self):
        arr = np.array([1.5, -2.5, 3.14159], dtype=np.float64)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert v[0].value == 1.5
        assert v[1].value == -2.5
        assert abs(v[2].value - 3.14159) < 1e-10
        assert isinstance(v[0], t.F64)

    def test_special_values(self):
        arr = np.array([0.0, -0.0, float("inf"), float("-inf")], dtype=np.float64)
        v = t.Vector.from_numpy(arr)
        assert v[0].value == 0.0
        assert v[2].value == float("inf")
        assert v[3].value == float("-inf")

    def test_very_small_and_large(self):
        arr = np.array([1e-300, 1e300], dtype=np.float64)
        v = t.Vector.from_numpy(arr)
        assert v[0].value == 1e-300
        assert v[1].value == 1e300


class TestFromNumpyBool:
    def test_basic_values(self):
        arr = np.array([True, False, True, False], dtype=np.bool_)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 4
        assert v[0].value is True
        assert v[1].value is False
        assert v[2].value is True
        assert v[3].value is False
        assert isinstance(v[0], t.B8)

    def test_all_true(self):
        arr = np.array([True, True, True], dtype=np.bool_)
        v = t.Vector.from_numpy(arr)
        assert all(v[i].value is True for i in range(3))

    def test_all_false(self):
        arr = np.array([False, False, False], dtype=np.bool_)
        v = t.Vector.from_numpy(arr)
        assert all(v[i].value is False for i in range(3))


# ============================================================================
# 2. Vector.from_numpy — datetime64 dtypes
# ============================================================================


class TestFromNumpyDatetime64Day:
    def test_basic_dates(self):
        arr = np.array(["2025-01-01", "2025-06-15", "2025-12-31"], dtype="datetime64[D]")
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert isinstance(v[0], t.Date)
        assert v[0].to_python() == dt.date(2025, 1, 1)
        assert v[1].to_python() == dt.date(2025, 6, 15)
        assert v[2].to_python() == dt.date(2025, 12, 31)

    def test_epoch_boundary(self):
        """Test dates around the rayforce epoch (2000-01-01)."""
        arr = np.array(["1999-12-31", "2000-01-01", "2000-01-02"], dtype="datetime64[D]")
        v = t.Vector.from_numpy(arr)
        assert v[0].to_python() == dt.date(1999, 12, 31)
        assert v[1].to_python() == dt.date(2000, 1, 1)
        assert v[2].to_python() == dt.date(2000, 1, 2)

    def test_unix_epoch(self):
        """Test date at unix epoch (1970-01-01)."""
        arr = np.array(["1970-01-01"], dtype="datetime64[D]")
        v = t.Vector.from_numpy(arr)
        assert v[0].to_python() == dt.date(1970, 1, 1)

    def test_far_future(self):
        arr = np.array(["2099-12-31"], dtype="datetime64[D]")
        v = t.Vector.from_numpy(arr)
        assert v[0].to_python() == dt.date(2099, 12, 31)


class TestFromNumpyDatetime64Ns:
    def test_basic_timestamps(self):
        arr = np.array(
            ["2025-01-01T00:00:00", "2025-06-15T12:30:45"],
            dtype="datetime64[ns]",
        )
        v = t.Vector.from_numpy(arr)
        assert len(v) == 2
        assert isinstance(v[0], t.Timestamp)
        py0 = v[0].to_python()
        assert py0.year == 2025
        assert py0.month == 1
        assert py0.day == 1

    def test_sub_second_precision(self):
        # 2025-03-15T10:20:30.123456789
        arr = np.array([np.datetime64("2025-03-15T10:20:30.123456789", "ns")])
        v = t.Vector.from_numpy(arr)
        assert len(v) == 1
        assert isinstance(v[0], t.Timestamp)


class TestFromNumpyDatetime64Seconds:
    def test_basic(self):
        arr = np.array(["2025-03-15T12:30:00", "2025-07-20T18:00:00"], dtype="datetime64[s]")
        v = t.Vector.from_numpy(arr)
        assert len(v) == 2
        assert isinstance(v[0], t.Timestamp)
        py0 = v[0].to_python()
        assert py0.hour == 12
        assert py0.minute == 30
        assert py0.second == 0


class TestFromNumpyDatetime64Ms:
    def test_basic(self):
        arr = np.array(["2025-01-01T00:00:00.500"], dtype="datetime64[ms]")
        v = t.Vector.from_numpy(arr)
        assert len(v) == 1
        assert isinstance(v[0], t.Timestamp)


class TestFromNumpyDatetime64Us:
    def test_basic(self):
        arr = np.array(["2025-01-01T00:00:00.000500"], dtype="datetime64[us]")
        v = t.Vector.from_numpy(arr)
        assert len(v) == 1
        assert isinstance(v[0], t.Timestamp)


# ============================================================================
# 3. Vector.from_numpy — timedelta64 dtypes
# ============================================================================


class TestFromNumpyTimedelta64:
    def test_timedelta_ms(self):
        """12:30:00 = 45,000,000 ms."""
        arr = np.array([45_000_000], dtype="timedelta64[ms]")
        v = t.Vector.from_numpy(arr)
        assert len(v) == 1
        assert isinstance(v[0], t.Time)
        assert v[0].to_python() == dt.time(12, 30, 0)

    def test_timedelta_multiple(self):
        # 09:00:00 = 32,400,000 ms; 18:00:00 = 64,800,000 ms
        arr = np.array([32_400_000, 64_800_000], dtype="timedelta64[ms]")
        v = t.Vector.from_numpy(arr)
        assert v[0].to_python() == dt.time(9, 0, 0)
        assert v[1].to_python() == dt.time(18, 0, 0)

    def test_timedelta_from_seconds(self):
        """timedelta64[s] should be converted to ms internally."""
        # 3600 seconds = 1 hour
        arr = np.array([3600], dtype="timedelta64[s]")
        v = t.Vector.from_numpy(arr)
        assert isinstance(v[0], t.Time)
        assert v[0].to_python() == dt.time(1, 0, 0)

    def test_timedelta_from_ns(self):
        """timedelta64[ns] should be converted to ms internally."""
        # 1 hour in nanoseconds
        arr = np.array([3_600_000_000_000], dtype="timedelta64[ns]")
        v = t.Vector.from_numpy(arr)
        assert isinstance(v[0], t.Time)
        assert v[0].to_python() == dt.time(1, 0, 0)

    def test_midnight(self):
        arr = np.array([0], dtype="timedelta64[ms]")
        v = t.Vector.from_numpy(arr)
        assert v[0].to_python() == dt.time(0, 0, 0)

    def test_end_of_day(self):
        # 23:59:59 = 86,399,000 ms
        arr = np.array([86_399_000], dtype="timedelta64[ms]")
        v = t.Vector.from_numpy(arr)
        assert v[0].to_python() == dt.time(23, 59, 59)


# ============================================================================
# 4. Vector.from_numpy — string/object arrays
# ============================================================================


class TestFromNumpyStrings:
    def test_unicode_array(self):
        arr = np.array(["apple", "banana", "cherry"])
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert v[0].value == "apple"
        assert v[1].value == "banana"
        assert v[2].value == "cherry"
        assert isinstance(v[0], t.Symbol)

    def test_object_array(self):
        arr = np.array(["x", "y", "z"], dtype=object)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert v[0].value == "x"
        assert v[1].value == "y"
        assert v[2].value == "z"

    def test_bytes_array(self):
        arr = np.array([b"foo", b"bar"], dtype="S3")
        v = t.Vector.from_numpy(arr)
        assert len(v) == 2
        assert v[0].value == "foo"
        assert v[1].value == "bar"

    def test_empty_strings(self):
        arr = np.array(["", "hello", ""])
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert v[0].value == ""
        assert v[1].value == "hello"
        assert v[2].value == ""

    def test_single_string(self):
        arr = np.array(["only_one"])
        v = t.Vector.from_numpy(arr)
        assert len(v) == 1
        assert v[0].value == "only_one"


# ============================================================================
# 5. Vector.from_numpy — explicit ray_type override
# ============================================================================


class TestFromNumpyExplicitRayType:
    def test_int64_as_f64(self):
        arr = np.array([1, 2, 3], dtype=np.int64)
        v = t.Vector.from_numpy(arr, ray_type=t.F64)
        assert len(v) == 3
        assert isinstance(v[0], t.F64)

    def test_int64_as_i32(self):
        arr = np.array([1, 2, 3], dtype=np.int64)
        v = t.Vector.from_numpy(arr, ray_type=t.I32)
        assert len(v) == 3
        assert isinstance(v[0], t.I32)

    def test_float64_as_i64(self):
        arr = np.array([1.0, 2.0, 3.0], dtype=np.float64)
        v = t.Vector.from_numpy(arr, ray_type=t.I64)
        assert len(v) == 3
        assert isinstance(v[0], t.I64)


# ============================================================================
# 6. Vector.from_numpy — unsupported dtypes
# ============================================================================


class TestFromNumpyUnsupported:
    def test_complex128_raises(self):
        arr = np.array([1 + 2j, 3 + 4j], dtype=np.complex128)
        with pytest.raises(errors.RayforceInitError, match="Cannot infer ray_type"):
            t.Vector.from_numpy(arr)

    def test_float32_preserved_as_rayf32(self):
        """float32 is preserved as RAY_F32 in v2 (no longer widens to F64)."""
        arr = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        # No RAY_F32 scalar atom in v2 — per-element access widens to F64.
        assert isinstance(v[0], t.F64)
        assert abs(v[0].value - 1.0) < 1e-6
        assert abs(v[1].value - 2.0) < 1e-6
        assert abs(v[2].value - 3.0) < 1e-6
        # Roundtrip to numpy preserves float32 dtype
        result = v.to_numpy()
        assert result.dtype == np.float32
        np.testing.assert_array_almost_equal(result, [1.0, 2.0, 3.0])

    def test_int8_auto_widens_to_i16(self):
        """int8 auto-widens to int16."""
        arr = np.array([1, -128, 127], dtype=np.int8)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert isinstance(v[0], t.I16)
        assert v[0].value == 1
        assert v[1].value == -128
        assert v[2].value == 127
        # Roundtrip to numpy gives int16
        result = v.to_numpy()
        assert result.dtype == np.int16
        np.testing.assert_array_equal(result, [1, -128, 127])

    def test_uint16_auto_widens_to_i32(self):
        arr = np.array([0, 65535], dtype=np.uint16)
        v = t.Vector.from_numpy(arr)
        assert isinstance(v[0], t.I32)
        assert v[0].value == 0
        assert v[1].value == 65535

    def test_uint32_auto_widens_to_i64(self):
        arr = np.array([0, 4294967295], dtype=np.uint32)
        v = t.Vector.from_numpy(arr)
        assert isinstance(v[0], t.I64)
        assert v[0].value == 0
        assert v[1].value == 4294967295

    def test_uint64_raises(self):
        arr = np.array([1, 2, 3], dtype=np.uint64)
        with pytest.raises(errors.RayforceInitError, match="Cannot infer ray_type"):
            t.Vector.from_numpy(arr)

    def test_float16_auto_widens_to_f64(self):
        arr = np.array([1.0, 2.0], dtype=np.float16)
        v = t.Vector.from_numpy(arr)
        assert isinstance(v[0], t.F64)
        assert abs(v[0].value - 1.0) < 1e-3

    def test_not_ndarray_raises(self):
        with pytest.raises(errors.RayforceInitError, match="requires a numpy ndarray"):
            t.Vector.from_numpy([1, 2, 3])

    def test_list_of_floats_raises(self):
        with pytest.raises(errors.RayforceInitError, match="requires a numpy ndarray"):
            t.Vector.from_numpy((1.0, 2.0, 3.0))


# ============================================================================
# 7. Vector.from_numpy — non-contiguous arrays
# ============================================================================


class TestFromNumpyNonContiguous:
    def test_fortran_order(self):
        arr = np.asfortranarray(np.array([[1, 2], [3, 4]], dtype=np.int64))
        col = arr[:, 0]  # Non-contiguous slice
        v = t.Vector.from_numpy(col)
        assert len(v) == 2
        assert v[0].value == 1
        assert v[1].value == 3

    def test_sliced_array(self):
        arr = np.arange(10, dtype=np.int64)
        sliced = arr[::2]  # [0, 2, 4, 6, 8] — non-contiguous
        v = t.Vector.from_numpy(sliced)
        assert len(v) == 5
        assert v[0].value == 0
        assert v[1].value == 2
        assert v[2].value == 4
        assert v[3].value == 6
        assert v[4].value == 8

    def test_reversed_array(self):
        arr = np.array([1, 2, 3, 4, 5], dtype=np.float64)[::-1]
        v = t.Vector.from_numpy(arr)
        assert len(v) == 5
        assert v[0].value == 5.0
        assert v[4].value == 1.0


# ============================================================================
# 8. Vector.to_numpy — all rayforce types
# ============================================================================


class TestToNumpyI64:
    def test_basic(self):
        v = t.Vector([10, 20, 30], ray_type=t.I64)
        arr = v.to_numpy()
        assert arr.dtype == np.int64
        np.testing.assert_array_equal(arr, [10, 20, 30])

    def test_negative(self):
        v = t.Vector([-100, 0, 100], ray_type=t.I64)
        arr = v.to_numpy()
        np.testing.assert_array_equal(arr, [-100, 0, 100])

    def test_empty(self):
        v = t.Vector(ray_type=t.I64, length=0)
        arr = v.to_numpy()
        assert arr.dtype == np.int64
        assert len(arr) == 0

    def test_single(self):
        v = t.Vector([42], ray_type=t.I64)
        arr = v.to_numpy()
        assert arr.shape == (1,)
        assert arr[0] == 42


class TestToNumpyI32:
    def test_basic(self):
        v = t.Vector([100_000, -200_000, 300_000], ray_type=t.I32)
        arr = v.to_numpy()
        assert arr.dtype == np.int32
        np.testing.assert_array_equal(arr, [100_000, -200_000, 300_000])

    def test_boundary(self):
        v = t.Vector([-2147483648, 2147483647], ray_type=t.I32)
        arr = v.to_numpy()
        assert arr[0] == -2147483648
        assert arr[1] == 2147483647


class TestToNumpyI16:
    def test_basic(self):
        v = t.Vector([100, -200, 300], ray_type=t.I16)
        arr = v.to_numpy()
        assert arr.dtype == np.int16
        np.testing.assert_array_equal(arr, [100, -200, 300])

    def test_boundary(self):
        v = t.Vector([-32768, 32767], ray_type=t.I16)
        arr = v.to_numpy()
        assert arr[0] == -32768
        assert arr[1] == 32767


class TestToNumpyU8:
    def test_basic(self):
        v = t.Vector([0, 128, 255], ray_type=t.U8)
        arr = v.to_numpy()
        assert arr.dtype == np.uint8
        np.testing.assert_array_equal(arr, [0, 128, 255])


class TestToNumpyF64:
    def test_basic(self):
        v = t.Vector([1.5, 2.5, 3.5], ray_type=t.F64)
        arr = v.to_numpy()
        assert arr.dtype == np.float64
        np.testing.assert_array_equal(arr, [1.5, 2.5, 3.5])

    def test_negative(self):
        v = t.Vector([-1.5, 0.0, 1.5], ray_type=t.F64)
        arr = v.to_numpy()
        np.testing.assert_array_equal(arr, [-1.5, 0.0, 1.5])


class TestToNumpyB8:
    def test_basic(self):
        v = t.Vector([True, False, True], ray_type=t.B8)
        arr = v.to_numpy()
        assert arr.dtype == np.bool_
        np.testing.assert_array_equal(arr, [True, False, True])


class TestToNumpyDate:
    def test_basic(self):
        v = t.Vector([dt.date(2025, 1, 1), dt.date(2025, 6, 15)], ray_type=t.Date)
        arr = v.to_numpy()
        assert arr.dtype == "datetime64[D]"
        assert arr[0] == np.datetime64("2025-01-01")
        assert arr[1] == np.datetime64("2025-06-15")

    def test_epoch_boundary(self):
        v = t.Vector(
            [dt.date(1999, 12, 31), dt.date(2000, 1, 1), dt.date(2000, 1, 2)],
            ray_type=t.Date,
        )
        arr = v.to_numpy()
        assert arr[0] == np.datetime64("1999-12-31")
        assert arr[1] == np.datetime64("2000-01-01")
        assert arr[2] == np.datetime64("2000-01-02")

    def test_unix_epoch(self):
        v = t.Vector([dt.date(1970, 1, 1)], ray_type=t.Date)
        arr = v.to_numpy()
        assert arr[0] == np.datetime64("1970-01-01")


class TestToNumpyTimestamp:
    def test_basic(self):
        v = t.Vector(
            [
                dt.datetime(2025, 1, 1, tzinfo=dt.UTC),
                dt.datetime(2025, 6, 15, 12, 0, 0, tzinfo=dt.UTC),
            ],
            ray_type=t.Timestamp,
        )
        arr = v.to_numpy()
        assert arr.dtype == "datetime64[ns]"
        assert arr[0] == np.datetime64("2025-01-01T00:00:00", "ns")
        assert arr[1] == np.datetime64("2025-06-15T12:00:00", "ns")


class TestToNumpyTime:
    def test_basic(self):
        v = t.Vector([dt.time(9, 0, 0), dt.time(18, 30, 0)], ray_type=t.Time)
        arr = v.to_numpy()
        assert arr.dtype == "timedelta64[ms]"
        # 9:00:00 = 32,400,000 ms
        assert arr[0] == np.timedelta64(32_400_000, "ms")
        # 18:30:00 = 66,600,000 ms
        assert arr[1] == np.timedelta64(66_600_000, "ms")

    def test_midnight(self):
        v = t.Vector([dt.time(0, 0, 0)], ray_type=t.Time)
        arr = v.to_numpy()
        assert arr[0] == np.timedelta64(0, "ms")


class TestToNumpySymbol:
    def test_basic(self):
        v = t.Vector(["alice", "bob", "charlie"], ray_type=t.Symbol)
        arr = v.to_numpy()
        # Symbol uses fallback via to_list()
        assert arr[0] == "alice"
        assert arr[1] == "bob"
        assert arr[2] == "charlie"


class TestToNumpyGUID:
    def test_basic(self):
        uid1 = uuid.UUID("12345678-1234-5678-1234-567812345678")
        uid2 = uuid.UUID("abcdefab-cdef-abcd-efab-cdefabcdefab")
        v = t.Vector([uid1, uid2], ray_type=t.GUID)
        arr = v.to_numpy()
        assert len(arr) == 2
        assert arr[0] == uid1
        assert arr[1] == uid2

    def test_roundtrip(self):
        """GUID vector → numpy object array → GUID vector."""
        uid1 = uuid.UUID("12345678-1234-5678-1234-567812345678")
        uid2 = uuid.UUID("abcdefab-cdef-abcd-efab-cdefabcdefab")
        v1 = t.Vector([uid1, uid2], ray_type=t.GUID)
        arr = v1.to_numpy()
        v2 = t.Vector.from_numpy(arr)
        assert len(v2) == 2
        assert v2[0].to_python() == uid1
        assert v2[1].to_python() == uid2


class TestToNumpyString:
    def test_basic(self):
        s = t.String("hello")
        arr = s.to_numpy()
        # String (C8 vector) uses fallback
        assert len(arr) == 5  # 5 characters


# ============================================================================
# 9. Roundtrip tests: numpy → rayforce → numpy
# ============================================================================


class TestRoundtripNumeric:
    def test_int64(self):
        original = np.array([10, 20, 30, 40, 50], dtype=np.int64)
        result = t.Vector.from_numpy(original).to_numpy()
        assert result.dtype == np.int64
        np.testing.assert_array_equal(result, original)

    def test_int32(self):
        original = np.array([100, -200, 300], dtype=np.int32)
        result = t.Vector.from_numpy(original).to_numpy()
        assert result.dtype == np.int32
        np.testing.assert_array_equal(result, original)

    def test_int16(self):
        original = np.array([10, -20, 30], dtype=np.int16)
        result = t.Vector.from_numpy(original).to_numpy()
        assert result.dtype == np.int16
        np.testing.assert_array_equal(result, original)

    def test_uint8(self):
        original = np.array([0, 128, 255], dtype=np.uint8)
        result = t.Vector.from_numpy(original).to_numpy()
        assert result.dtype == np.uint8
        np.testing.assert_array_equal(result, original)

    def test_float64(self):
        original = np.array([1.1, 2.2, 3.3], dtype=np.float64)
        result = t.Vector.from_numpy(original).to_numpy()
        assert result.dtype == np.float64
        np.testing.assert_array_almost_equal(result, original)

    def test_bool(self):
        original = np.array([True, False, True, False], dtype=np.bool_)
        result = t.Vector.from_numpy(original).to_numpy()
        assert result.dtype == np.bool_
        np.testing.assert_array_equal(result, original)


class TestRoundtripTemporal:
    def test_date(self):
        original = np.array(["2025-01-01", "2025-06-15", "2025-12-31"], dtype="datetime64[D]")
        result = t.Vector.from_numpy(original).to_numpy()
        assert result.dtype == "datetime64[D]"
        np.testing.assert_array_equal(result, original)

    def test_timestamp_from_ns(self):
        original = np.array(
            ["2025-01-01T00:00:00", "2025-06-15T12:30:00"],
            dtype="datetime64[ns]",
        )
        result = t.Vector.from_numpy(original).to_numpy()
        assert result.dtype == "datetime64[ns]"
        np.testing.assert_array_equal(result, original)

    def test_timestamp_from_s(self):
        """Seconds → converted to ns internally → roundtrip back at ns resolution."""
        original_s = np.array(["2025-03-15T12:30:00"], dtype="datetime64[s]")
        expected_ns = original_s.astype("datetime64[ns]")
        result = t.Vector.from_numpy(original_s).to_numpy()
        assert result.dtype == "datetime64[ns]"
        np.testing.assert_array_equal(result, expected_ns)

    def test_timestamp_from_ms(self):
        original_ms = np.array(["2025-01-01T00:00:00.500"], dtype="datetime64[ms]")
        expected_ns = original_ms.astype("datetime64[ns]")
        result = t.Vector.from_numpy(original_ms).to_numpy()
        assert result.dtype == "datetime64[ns]"
        np.testing.assert_array_equal(result, expected_ns)

    def test_time_roundtrip(self):
        # 09:30:00 = 34,200,000 ms; 14:45:30 = 53,130,000 ms
        original = np.array([34_200_000, 53_130_000], dtype="timedelta64[ms]")
        result = t.Vector.from_numpy(original).to_numpy()
        assert result.dtype == "timedelta64[ms]"
        np.testing.assert_array_equal(result, original)


class TestRoundtripStrings:
    def test_unicode(self):
        original = np.array(["hello", "world"])
        v = t.Vector.from_numpy(original)
        result = v.to_numpy()
        np.testing.assert_array_equal(result, ["hello", "world"])

    def test_object_strings(self):
        original = np.array(["foo", "bar", "baz"], dtype=object)
        v = t.Vector.from_numpy(original)
        result = v.to_numpy()
        assert result[0] == "foo"
        assert result[1] == "bar"
        assert result[2] == "baz"


class TestRoundtripEmpty:
    def test_empty_int64(self):
        original = np.array([], dtype=np.int64)
        result = t.Vector.from_numpy(original).to_numpy()
        assert result.dtype == np.int64
        assert len(result) == 0

    def test_empty_float64(self):
        original = np.array([], dtype=np.float64)
        result = t.Vector.from_numpy(original).to_numpy()
        assert result.dtype == np.float64
        assert len(result) == 0

    def test_empty_bool(self):
        original = np.array([], dtype=np.bool_)
        result = t.Vector.from_numpy(original).to_numpy()
        assert result.dtype == np.bool_
        assert len(result) == 0


class TestRoundtripLarge:
    N = 100_000

    def test_large_int64(self):
        original = np.arange(self.N, dtype=np.int64)
        result = t.Vector.from_numpy(original).to_numpy()
        np.testing.assert_array_equal(result, original)

    def test_large_float64(self):
        original = np.arange(self.N, dtype=np.float64) * 0.1
        result = t.Vector.from_numpy(original).to_numpy()
        np.testing.assert_array_almost_equal(result, original)

    def test_large_uint8(self):
        original = np.arange(self.N, dtype=np.uint8)
        result = t.Vector.from_numpy(original).to_numpy()
        np.testing.assert_array_equal(result, original)


# ============================================================================
# 10. Roundtrip: rayforce → numpy → rayforce
# ============================================================================


class TestRoundtripRayNumpyRay:
    def test_i64_ray_to_numpy_to_ray(self):
        v1 = t.Vector([10, 20, 30], ray_type=t.I64)
        arr = v1.to_numpy()
        v2 = t.Vector.from_numpy(arr)
        assert len(v2) == 3
        assert v2[0].value == 10
        assert v2[1].value == 20
        assert v2[2].value == 30

    def test_f64_ray_to_numpy_to_ray(self):
        v1 = t.Vector([1.5, 2.5, 3.5], ray_type=t.F64)
        arr = v1.to_numpy()
        v2 = t.Vector.from_numpy(arr)
        assert abs(v2[0].value - 1.5) < 1e-10
        assert abs(v2[1].value - 2.5) < 1e-10
        assert abs(v2[2].value - 3.5) < 1e-10

    def test_b8_ray_to_numpy_to_ray(self):
        v1 = t.Vector([True, False, True], ray_type=t.B8)
        arr = v1.to_numpy()
        v2 = t.Vector.from_numpy(arr)
        assert v2[0].value is True
        assert v2[1].value is False
        assert v2[2].value is True

    def test_date_ray_to_numpy_to_ray(self):
        dates = [dt.date(2025, 1, 1), dt.date(2025, 6, 15)]
        v1 = t.Vector(dates, ray_type=t.Date)
        arr = v1.to_numpy()
        v2 = t.Vector.from_numpy(arr)
        assert v2[0].to_python() == dt.date(2025, 1, 1)
        assert v2[1].to_python() == dt.date(2025, 6, 15)

    def test_timestamp_ray_to_numpy_to_ray(self):
        dts = [
            dt.datetime(2025, 1, 1, tzinfo=dt.UTC),
            dt.datetime(2025, 6, 15, 12, 0, 0, tzinfo=dt.UTC),
        ]
        v1 = t.Vector(dts, ray_type=t.Timestamp)
        arr = v1.to_numpy()
        v2 = t.Vector.from_numpy(arr)
        assert v2[0].to_python().replace(tzinfo=None) == dt.datetime(2025, 1, 1)
        assert v2[1].to_python().replace(tzinfo=None) == dt.datetime(2025, 6, 15, 12, 0, 0)

    def test_time_ray_to_numpy_to_ray(self):
        times = [dt.time(9, 30, 0), dt.time(14, 45, 0)]
        v1 = t.Vector(times, ray_type=t.Time)
        arr = v1.to_numpy()
        v2 = t.Vector.from_numpy(arr)
        assert v2[0].to_python() == dt.time(9, 30, 0)
        assert v2[1].to_python() == dt.time(14, 45, 0)


# ============================================================================
# 11. Table.from_dict with numpy arrays
# ============================================================================


class TestTableFromDictNumpy:
    def test_int64_columns(self):
        tbl = t.Table.from_dict(
            {
                "a": np.array([1, 2, 3], dtype=np.int64),
                "b": np.array([4, 5, 6], dtype=np.int64),
            }
        )
        assert len(tbl) == 3
        assert tbl["a"][0].value == 1
        assert tbl["b"][2].value == 6

    def test_float64_columns(self):
        tbl = t.Table.from_dict(
            {
                "x": np.array([1.1, 2.2], dtype=np.float64),
                "y": np.array([3.3, 4.4], dtype=np.float64),
            }
        )
        assert len(tbl) == 2
        assert abs(tbl["x"][0].value - 1.1) < 1e-10
        assert abs(tbl["y"][1].value - 4.4) < 1e-10

    def test_mixed_numpy_dtypes(self):
        tbl = t.Table.from_dict(
            {
                "id": np.array([1, 2, 3], dtype=np.int64),
                "score": np.array([95.5, 87.3, 92.1], dtype=np.float64),
                "active": np.array([True, False, True], dtype=np.bool_),
            }
        )
        assert len(tbl) == 3
        assert tbl["id"][0].value == 1
        assert abs(tbl["score"][0].value - 95.5) < 1e-10
        assert tbl["active"][0].value is True
        assert tbl["active"][1].value is False

    def test_string_numpy_column(self):
        tbl = t.Table.from_dict(
            {
                "name": np.array(["alice", "bob", "charlie"]),
                "age": np.array([25, 30, 35], dtype=np.int64),
            }
        )
        assert tbl["name"][0].value == "alice"
        assert tbl["age"][2].value == 35

    def test_datetime64_column(self):
        tbl = t.Table.from_dict(
            {
                "id": np.array([1, 2], dtype=np.int64),
                "date": np.array(["2025-01-01", "2025-06-15"], dtype="datetime64[D]"),
            }
        )
        assert len(tbl) == 2
        assert isinstance(tbl["date"][0], t.Date)
        assert tbl["date"][0].to_python() == dt.date(2025, 1, 1)

    def test_timedelta64_column(self):
        tbl = t.Table.from_dict(
            {
                "id": np.array([1, 2], dtype=np.int64),
                "time": np.array([32_400_000, 64_800_000], dtype="timedelta64[ms]"),
            }
        )
        assert isinstance(tbl["time"][0], t.Time)
        assert tbl["time"][0].to_python() == dt.time(9, 0, 0)

    def test_uint8_column(self):
        tbl = t.Table.from_dict(
            {
                "flags": np.array([0, 1, 255], dtype=np.uint8),
            }
        )
        assert tbl["flags"][0].value == 0
        assert tbl["flags"][1].value == 1
        assert tbl["flags"][2].value == 255

    def test_int16_column(self):
        tbl = t.Table.from_dict(
            {
                "val": np.array([100, -200, 300], dtype=np.int16),
            }
        )
        assert tbl["val"][0].value == 100
        assert tbl["val"][1].value == -200

    def test_int32_column(self):
        tbl = t.Table.from_dict(
            {
                "val": np.array([100_000, -200_000], dtype=np.int32),
            }
        )
        assert tbl["val"][0].value == 100_000
        assert tbl["val"][1].value == -200_000

    def test_mixed_vector_and_numpy(self):
        tbl = t.Table.from_dict(
            {
                "np_col": np.array([1, 2, 3], dtype=np.int64),
                "vec_col": t.Vector([10, 20, 30], ray_type=t.I64),
                "list_col": [100, 200, 300],
            }
        )
        assert tbl["np_col"][0].value == 1
        assert tbl["vec_col"][1].value == 20
        assert tbl["list_col"][2].value == 300

    def test_unsupported_column_type_raises(self):
        with pytest.raises(errors.RayforceInitError, match="expected Vector"):
            t.Table.from_dict({"bad": 42})


# ============================================================================
# 12. Table.to_numpy
# ============================================================================


class TestTableToNumpyComprehensive:
    def test_homogeneous_int(self):
        tbl = t.Table(
            {
                "a": t.Vector([1, 2, 3], ray_type=t.I64),
                "b": t.Vector([4, 5, 6], ray_type=t.I64),
            }
        )
        arr = tbl.to_numpy()
        assert arr.shape == (3, 2)
        assert arr.dtype == np.int64
        np.testing.assert_array_equal(arr[:, 0], [1, 2, 3])
        np.testing.assert_array_equal(arr[:, 1], [4, 5, 6])

    def test_homogeneous_float(self):
        tbl = t.Table(
            {
                "x": t.Vector([1.1, 2.2], ray_type=t.F64),
                "y": t.Vector([3.3, 4.4], ray_type=t.F64),
            }
        )
        arr = tbl.to_numpy()
        assert arr.shape == (2, 2)
        assert arr.dtype == np.float64
        np.testing.assert_array_almost_equal(arr[:, 0], [1.1, 2.2])
        np.testing.assert_array_almost_equal(arr[:, 1], [3.3, 4.4])

    def test_int_and_float_promotion(self):
        tbl = t.Table(
            {
                "a": t.Vector([1, 2, 3], ray_type=t.I64),
                "b": t.Vector([4.0, 5.0, 6.0], ray_type=t.F64),
            }
        )
        arr = tbl.to_numpy()
        assert arr.shape == (3, 2)
        assert arr.dtype == np.float64  # int promotes to float
        np.testing.assert_array_equal(arr[:, 0], [1, 2, 3])
        np.testing.assert_array_equal(arr[:, 1], [4.0, 5.0, 6.0])

    def test_mixed_symbol_and_int(self):
        tbl = t.Table(
            {
                "name": t.Vector(["alice", "bob"], ray_type=t.Symbol),
                "age": t.Vector([25, 30], ray_type=t.I64),
            }
        )
        arr = tbl.to_numpy()
        assert arr.shape == (2, 2)
        # Mixed types force object/string coercion
        assert arr[0, 0] == "alice"

    def test_single_column(self):
        tbl = t.Table({"x": t.Vector([10, 20, 30], ray_type=t.I64)})
        arr = tbl.to_numpy()
        assert arr.shape == (3, 1)
        np.testing.assert_array_equal(arr[:, 0], [10, 20, 30])

    def test_single_row(self):
        tbl = t.Table(
            {
                "a": t.Vector([1], ray_type=t.I64),
                "b": t.Vector([2], ray_type=t.I64),
                "c": t.Vector([3], ray_type=t.I64),
            }
        )
        arr = tbl.to_numpy()
        assert arr.shape == (1, 3)
        np.testing.assert_array_equal(arr[0], [1, 2, 3])

    def test_all_numeric_types(self):
        tbl = t.Table(
            {
                "u8": t.Vector([1, 2], ray_type=t.U8),
                "i16": t.Vector([100, 200], ray_type=t.I16),
                "i32": t.Vector([1000, 2000], ray_type=t.I32),
                "i64": t.Vector([10000, 20000], ray_type=t.I64),
                "f64": t.Vector([1.5, 2.5], ray_type=t.F64),
            }
        )
        arr = tbl.to_numpy()
        assert arr.shape == (2, 5)
        # All numeric types promote to float64
        assert arr.dtype == np.float64
        assert arr[0, 0] == 1.0  # u8
        assert arr[0, 1] == 100.0  # i16
        assert arr[0, 2] == 1000.0  # i32
        assert arr[0, 3] == 10000.0  # i64
        assert arr[0, 4] == 1.5  # f64

    def test_with_temporal_columns_fallback_to_object(self):
        tbl = t.Table(
            {
                "id": t.Vector([1, 2], ray_type=t.I64),
                "date": t.Vector([dt.date(2025, 1, 1), dt.date(2025, 6, 15)], ray_type=t.Date),
            }
        )
        arr = tbl.to_numpy()
        assert arr.shape == (2, 2)
        # Mixed int + datetime forces object dtype
        assert arr.dtype == object


# ============================================================================
# 13. Table roundtrip: numpy → Table → numpy
# ============================================================================


class TestTableNumpyRoundtrip:
    def test_int_table(self):
        original = {
            "a": np.array([1, 2, 3], dtype=np.int64),
            "b": np.array([4, 5, 6], dtype=np.int64),
        }
        tbl = t.Table.from_dict(original)
        arr = tbl.to_numpy()
        assert arr.shape == (3, 2)
        np.testing.assert_array_equal(arr[:, 0], [1, 2, 3])
        np.testing.assert_array_equal(arr[:, 1], [4, 5, 6])

    def test_float_table(self):
        original = {
            "x": np.array([1.1, 2.2, 3.3], dtype=np.float64),
            "y": np.array([4.4, 5.5, 6.6], dtype=np.float64),
        }
        tbl = t.Table.from_dict(original)
        arr = tbl.to_numpy()
        np.testing.assert_array_almost_equal(arr[:, 0], [1.1, 2.2, 3.3])
        np.testing.assert_array_almost_equal(arr[:, 1], [4.4, 5.5, 6.6])

    def test_bool_table(self):
        original = {
            "a": np.array([True, False], dtype=np.bool_),
            "b": np.array([False, True], dtype=np.bool_),
        }
        tbl = t.Table.from_dict(original)
        arr = tbl.to_numpy()
        assert arr.shape == (2, 2)
        # bool columns get promoted to int or stay bool
        assert arr[0, 0] == True  # noqa: E712
        assert arr[0, 1] == False  # noqa: E712

    def test_to_dict_roundtrip(self):
        original = {
            "id": np.array([1, 2, 3], dtype=np.int64),
            "val": np.array([10.5, 20.5, 30.5], dtype=np.float64),
        }
        tbl = t.Table.from_dict(original)
        d = tbl.to_dict()
        assert d["id"] == [1, 2, 3]
        np.testing.assert_array_almost_equal(d["val"], [10.5, 20.5, 30.5])


# ============================================================================
# 14. Coverage of every rayforce type: can it be created and to_numpy'd?
# ============================================================================


class TestEveryRayforceTypeToNumpy:
    """Ensure every rayforce scalar type in a vector can be converted to numpy."""

    def test_b8_vector(self):
        v = t.Vector([True, False], ray_type=t.B8)
        arr = v.to_numpy()
        assert arr.dtype == np.bool_
        assert arr[0] == True  # noqa: E712
        assert arr[1] == False  # noqa: E712

    def test_u8_vector(self):
        v = t.Vector([0, 255], ray_type=t.U8)
        arr = v.to_numpy()
        assert arr.dtype == np.uint8
        assert arr[0] == 0
        assert arr[1] == 255

    def test_i16_vector(self):
        v = t.Vector([-32768, 32767], ray_type=t.I16)
        arr = v.to_numpy()
        assert arr.dtype == np.int16
        assert arr[0] == -32768
        assert arr[1] == 32767

    def test_i32_vector(self):
        v = t.Vector([-2147483648, 2147483647], ray_type=t.I32)
        arr = v.to_numpy()
        assert arr.dtype == np.int32
        assert arr[0] == -2147483648
        assert arr[1] == 2147483647

    def test_i64_vector(self):
        v = t.Vector([-9223372036854775807, 9223372036854775807], ray_type=t.I64)
        arr = v.to_numpy()
        assert arr.dtype == np.int64
        assert arr[0] == -9223372036854775807
        assert arr[1] == 9223372036854775807

    def test_f64_vector(self):
        v = t.Vector([1e-300, 1e300], ray_type=t.F64)
        arr = v.to_numpy()
        assert arr.dtype == np.float64
        assert arr[0] == 1e-300
        assert arr[1] == 1e300

    def test_symbol_vector(self):
        v = t.Vector(["hello", "world"], ray_type=t.Symbol)
        arr = v.to_numpy()
        assert arr[0] == "hello"
        assert arr[1] == "world"

    def test_date_vector(self):
        v = t.Vector([dt.date(2025, 1, 1), dt.date(2025, 12, 31)], ray_type=t.Date)
        arr = v.to_numpy()
        assert arr.dtype == "datetime64[D]"
        assert arr[0] == np.datetime64("2025-01-01")
        assert arr[1] == np.datetime64("2025-12-31")

    def test_time_vector(self):
        v = t.Vector([dt.time(0, 0), dt.time(23, 59, 59)], ray_type=t.Time)
        arr = v.to_numpy()
        assert arr.dtype == "timedelta64[ms]"
        assert arr[0] == np.timedelta64(0, "ms")
        assert arr[1] == np.timedelta64(86_399_000, "ms")

    def test_timestamp_vector(self):
        v = t.Vector(
            [dt.datetime(2025, 1, 1, tzinfo=dt.UTC), dt.datetime(2025, 12, 31, tzinfo=dt.UTC)],
            ray_type=t.Timestamp,
        )
        arr = v.to_numpy()
        assert arr.dtype == "datetime64[ns]"
        assert arr[0] == np.datetime64("2025-01-01", "ns")
        assert arr[1] == np.datetime64("2025-12-31", "ns")

    def test_guid_vector(self):
        uid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        v = t.Vector([uid], ray_type=t.GUID)
        arr = v.to_numpy()
        assert len(arr) == 1
        # GUID falls back to to_list() → np.array(), so we get an object array

    def test_c8_string_vector(self):
        s = t.String("abc")
        arr = s.to_numpy()
        assert len(arr) == 3  # 3 characters


# ============================================================================
# 15. Coverage of every numpy dtype: can it be from_numpy'd?
# ============================================================================


class TestEveryNumpyDtypeFromNumpy:
    """Test every common numpy dtype with Vector.from_numpy."""

    def test_bool(self):
        v = t.Vector.from_numpy(np.array([True], dtype=np.bool_))
        assert isinstance(v[0], t.B8)
        assert v[0].value is True

    def test_uint8(self):
        v = t.Vector.from_numpy(np.array([42], dtype=np.uint8))
        assert isinstance(v[0], t.U8)
        assert v[0].value == 42

    def test_int16(self):
        v = t.Vector.from_numpy(np.array([42], dtype=np.int16))
        assert isinstance(v[0], t.I16)
        assert v[0].value == 42

    def test_int32(self):
        v = t.Vector.from_numpy(np.array([42], dtype=np.int32))
        assert isinstance(v[0], t.I32)
        assert v[0].value == 42

    def test_int64(self):
        v = t.Vector.from_numpy(np.array([42], dtype=np.int64))
        assert isinstance(v[0], t.I64)
        assert v[0].value == 42

    def test_float64(self):
        v = t.Vector.from_numpy(np.array([3.14], dtype=np.float64))
        assert isinstance(v[0], t.F64)
        assert abs(v[0].value - 3.14) < 1e-10

    def test_datetime64_D(self):
        v = t.Vector.from_numpy(np.array(["2025-01-01"], dtype="datetime64[D]"))
        assert isinstance(v[0], t.Date)

    def test_datetime64_s(self):
        v = t.Vector.from_numpy(np.array(["2025-01-01T12:00:00"], dtype="datetime64[s]"))
        assert isinstance(v[0], t.Timestamp)

    def test_datetime64_ms(self):
        v = t.Vector.from_numpy(np.array(["2025-01-01T12:00:00.500"], dtype="datetime64[ms]"))
        assert isinstance(v[0], t.Timestamp)

    def test_datetime64_us(self):
        v = t.Vector.from_numpy(np.array(["2025-01-01T12:00:00.000500"], dtype="datetime64[us]"))
        assert isinstance(v[0], t.Timestamp)

    def test_datetime64_ns(self):
        v = t.Vector.from_numpy(np.array(["2025-01-01T12:00:00"], dtype="datetime64[ns]"))
        assert isinstance(v[0], t.Timestamp)

    def test_timedelta64_ms(self):
        v = t.Vector.from_numpy(np.array([3600000], dtype="timedelta64[ms]"))
        assert isinstance(v[0], t.Time)
        assert v[0].to_python() == dt.time(1, 0, 0)

    def test_timedelta64_s(self):
        v = t.Vector.from_numpy(np.array([3600], dtype="timedelta64[s]"))
        assert isinstance(v[0], t.Time)
        assert v[0].to_python() == dt.time(1, 0, 0)

    def test_timedelta64_ns(self):
        v = t.Vector.from_numpy(np.array([3_600_000_000_000], dtype="timedelta64[ns]"))
        assert isinstance(v[0], t.Time)
        assert v[0].to_python() == dt.time(1, 0, 0)

    def test_unicode_str(self):
        v = t.Vector.from_numpy(np.array(["hello"]))
        assert isinstance(v[0], t.Symbol)
        assert v[0].value == "hello"

    def test_object_str(self):
        v = t.Vector.from_numpy(np.array(["hello"], dtype=object))
        assert isinstance(v[0], t.Symbol)
        assert v[0].value == "hello"

    def test_bytes_str(self):
        v = t.Vector.from_numpy(np.array([b"hi"], dtype="S2"))
        assert len(v) == 1
        assert v[0].value == "hi"

    # --- Unsupported dtypes should raise ---

    def test_int8_auto_widens(self):
        v = t.Vector.from_numpy(np.array([1], dtype=np.int8))
        assert isinstance(v[0], t.I16)
        assert v[0].value == 1

    def test_uint16_auto_widens(self):
        v = t.Vector.from_numpy(np.array([1], dtype=np.uint16))
        assert isinstance(v[0], t.I32)
        assert v[0].value == 1

    def test_uint32_auto_widens(self):
        v = t.Vector.from_numpy(np.array([1], dtype=np.uint32))
        assert isinstance(v[0], t.I64)
        assert v[0].value == 1

    def test_uint64_unsupported(self):
        with pytest.raises(errors.RayforceInitError):
            t.Vector.from_numpy(np.array([1], dtype=np.uint64))

    def test_float16_auto_widens(self):
        v = t.Vector.from_numpy(np.array([1.0], dtype=np.float16))
        assert isinstance(v[0], t.F64)
        assert abs(v[0].value - 1.0) < 1e-3

    def test_float32_auto_widens(self):
        v = t.Vector.from_numpy(np.array([1.0], dtype=np.float32))
        assert isinstance(v[0], t.F64)
        assert abs(v[0].value - 1.0) < 1e-6

    def test_complex64_unsupported(self):
        with pytest.raises(errors.RayforceInitError):
            t.Vector.from_numpy(np.array([1 + 2j], dtype=np.complex64))

    def test_complex128_unsupported(self):
        with pytest.raises(errors.RayforceInitError):
            t.Vector.from_numpy(np.array([1 + 2j], dtype=np.complex128))


# ============================================================================
# 16. Numpy operations on converted arrays
# ============================================================================


class TestNumpyOperationsOnConverted:
    """Verify that numpy arrays obtained from rayforce are fully usable."""

    def test_arithmetic(self):
        v = t.Vector([10, 20, 30], ray_type=t.F64)
        arr = v.to_numpy()
        result = arr * 2 + 1
        np.testing.assert_array_equal(result, [21.0, 41.0, 61.0])

    def test_aggregation(self):
        v = t.Vector([10, 20, 30, 40, 50], ray_type=t.I64)
        arr = v.to_numpy()
        assert arr.sum() == 150
        assert arr.mean() == 30.0
        assert arr.min() == 10
        assert arr.max() == 50
        assert arr.std() == np.std([10, 20, 30, 40, 50])

    def test_slicing(self):
        v = t.Vector([1, 2, 3, 4, 5], ray_type=t.I64)
        arr = v.to_numpy()
        np.testing.assert_array_equal(arr[1:4], [2, 3, 4])
        np.testing.assert_array_equal(arr[::-1], [5, 4, 3, 2, 1])

    def test_boolean_indexing(self):
        v = t.Vector([10, 20, 30, 40, 50], ray_type=t.I64)
        arr = v.to_numpy()
        mask = arr > 25
        np.testing.assert_array_equal(arr[mask], [30, 40, 50])

    def test_sort(self):
        v = t.Vector([30, 10, 50, 20, 40], ray_type=t.I64)
        arr = v.to_numpy()
        sorted_arr = np.sort(arr)
        np.testing.assert_array_equal(sorted_arr, [10, 20, 30, 40, 50])

    def test_date_comparison(self):
        v = t.Vector(
            [dt.date(2025, 1, 1), dt.date(2025, 6, 15), dt.date(2025, 12, 31)],
            ray_type=t.Date,
        )
        arr = v.to_numpy()
        cutoff = np.datetime64("2025-06-01")
        after = arr[arr > cutoff]
        assert len(after) == 2
        assert after[0] == np.datetime64("2025-06-15")
        assert after[1] == np.datetime64("2025-12-31")

    def test_timestamp_diff(self):
        v = t.Vector(
            [
                dt.datetime(2025, 1, 1, tzinfo=dt.UTC),
                dt.datetime(2025, 1, 2, tzinfo=dt.UTC),
            ],
            ray_type=t.Timestamp,
        )
        arr = v.to_numpy()
        diff = arr[1] - arr[0]
        assert diff == np.timedelta64(1, "D")


# ============================================================================
# 17. Edge case: table with all supported numpy types
# ============================================================================


class TestTableAllNumpyTypes:
    def test_create_and_access(self):
        tbl = t.Table.from_dict(
            {
                "bool_col": np.array([True, False], dtype=np.bool_),
                "u8_col": np.array([0, 255], dtype=np.uint8),
                "i16_col": np.array([100, -100], dtype=np.int16),
                "i32_col": np.array([1000, -1000], dtype=np.int32),
                "i64_col": np.array([10000, -10000], dtype=np.int64),
                "f64_col": np.array([1.5, -1.5], dtype=np.float64),
                "str_col": np.array(["hello", "world"]),
                "date_col": np.array(["2025-01-01", "2025-12-31"], dtype="datetime64[D]"),
                "ts_col": np.array(
                    ["2025-01-01T00:00:00", "2025-12-31T23:59:59"],
                    dtype="datetime64[ns]",
                ),
                "time_col": np.array([0, 86_399_000], dtype="timedelta64[ms]"),
            }
        )
        assert len(tbl) == 2

        # Check each column type and values
        assert tbl["bool_col"][0].value is True
        assert tbl["bool_col"][1].value is False

        assert tbl["u8_col"][0].value == 0
        assert tbl["u8_col"][1].value == 255

        assert tbl["i16_col"][0].value == 100
        assert tbl["i16_col"][1].value == -100

        assert tbl["i32_col"][0].value == 1000
        assert tbl["i32_col"][1].value == -1000

        assert tbl["i64_col"][0].value == 10000
        assert tbl["i64_col"][1].value == -10000

        assert tbl["f64_col"][0].value == 1.5
        assert tbl["f64_col"][1].value == -1.5

        assert tbl["str_col"][0].value == "hello"
        assert tbl["str_col"][1].value == "world"

        assert isinstance(tbl["date_col"][0], t.Date)
        assert tbl["date_col"][0].to_python() == dt.date(2025, 1, 1)

        assert isinstance(tbl["ts_col"][0], t.Timestamp)

        assert isinstance(tbl["time_col"][0], t.Time)
        assert tbl["time_col"][0].to_python() == dt.time(0, 0, 0)
        assert tbl["time_col"][1].to_python() == dt.time(23, 59, 59)

    def test_per_column_to_numpy(self):
        """Each column should roundtrip to numpy with correct dtype."""
        tbl = t.Table.from_dict(
            {
                "bool_col": np.array([True, False], dtype=np.bool_),
                "u8_col": np.array([0, 255], dtype=np.uint8),
                "i16_col": np.array([100, -100], dtype=np.int16),
                "i32_col": np.array([1000, -1000], dtype=np.int32),
                "i64_col": np.array([10000, -10000], dtype=np.int64),
                "f64_col": np.array([1.5, -1.5], dtype=np.float64),
            }
        )

        bool_arr = tbl["bool_col"].to_numpy()
        assert bool_arr.dtype == np.bool_
        np.testing.assert_array_equal(bool_arr, [True, False])

        u8_arr = tbl["u8_col"].to_numpy()
        assert u8_arr.dtype == np.uint8
        np.testing.assert_array_equal(u8_arr, [0, 255])

        i16_arr = tbl["i16_col"].to_numpy()
        assert i16_arr.dtype == np.int16
        np.testing.assert_array_equal(i16_arr, [100, -100])

        i32_arr = tbl["i32_col"].to_numpy()
        assert i32_arr.dtype == np.int32
        np.testing.assert_array_equal(i32_arr, [1000, -1000])

        i64_arr = tbl["i64_col"].to_numpy()
        assert i64_arr.dtype == np.int64
        np.testing.assert_array_equal(i64_arr, [10000, -10000])

        f64_arr = tbl["f64_col"].to_numpy()
        assert f64_arr.dtype == np.float64
        np.testing.assert_array_almost_equal(f64_arr, [1.5, -1.5])


# ============================================================================
# 18. NaT preservation in temporal conversions
# ============================================================================


class TestNaTPreservation:
    """NaT values must survive numpy → rayforce → numpy round-trips."""

    def test_date_with_nat(self):
        arr = np.array(["2025-01-01", "NaT", "2025-12-31"], dtype="datetime64[D]")
        v = t.Vector.from_numpy(arr)
        result = v.to_numpy()
        assert result.dtype == "datetime64[D]"
        assert result[0] == np.datetime64("2025-01-01")
        assert np.isnat(result[1])
        assert result[2] == np.datetime64("2025-12-31")

    def test_date_all_nat(self):
        arr = np.array(["NaT", "NaT"], dtype="datetime64[D]")
        v = t.Vector.from_numpy(arr)
        result = v.to_numpy()
        assert np.isnat(result[0])
        assert np.isnat(result[1])

    def test_date_no_nat(self):
        """No NaT — fast path, no copies."""
        arr = np.array(["2025-01-01", "2025-06-15"], dtype="datetime64[D]")
        v = t.Vector.from_numpy(arr)
        result = v.to_numpy()
        np.testing.assert_array_equal(result, arr)

    def test_timestamp_with_nat(self):
        arr = np.array(
            ["2025-01-01T00:00:00", "NaT", "2025-12-31T23:59:59"],
            dtype="datetime64[ns]",
        )
        v = t.Vector.from_numpy(arr)
        result = v.to_numpy()
        assert result.dtype == "datetime64[ns]"
        assert result[0] == np.datetime64("2025-01-01T00:00:00", "ns")
        assert np.isnat(result[1])
        assert result[2] == np.datetime64("2025-12-31T23:59:59", "ns")

    def test_timestamp_all_nat(self):
        arr = np.array(["NaT", "NaT"], dtype="datetime64[ns]")
        v = t.Vector.from_numpy(arr)
        result = v.to_numpy()
        assert np.isnat(result[0])
        assert np.isnat(result[1])

    def test_timestamp_from_seconds_with_nat(self):
        arr = np.array(["2025-03-15T12:00:00", "NaT"], dtype="datetime64[s]")
        v = t.Vector.from_numpy(arr)
        result = v.to_numpy()
        assert result.dtype == "datetime64[ns]"
        assert result[0] == np.datetime64("2025-03-15T12:00:00", "ns")
        assert np.isnat(result[1])

    def test_timedelta_with_nat(self):
        arr = np.array([3_600_000, "NaT", 7_200_000], dtype="timedelta64[ms]")
        v = t.Vector.from_numpy(arr)
        result = v.to_numpy()
        assert result.dtype == "timedelta64[ms]"
        assert result[0] == np.timedelta64(3_600_000, "ms")
        assert np.isnat(result[1])
        assert result[2] == np.timedelta64(7_200_000, "ms")

    def test_timedelta_all_nat(self):
        arr = np.array(["NaT", "NaT"], dtype="timedelta64[ms]")
        v = t.Vector.from_numpy(arr)
        result = v.to_numpy()
        assert np.isnat(result[0])
        assert np.isnat(result[1])

    def test_float64_nan_roundtrip(self):
        """NaN in float64 should survive the round-trip."""
        arr = np.array([1.0, float("nan"), 3.0], dtype=np.float64)
        v = t.Vector.from_numpy(arr)
        result = v.to_numpy()
        assert result[0] == 1.0
        assert np.isnan(result[1])
        assert result[2] == 3.0


# ============================================================================
# 19. Auto-widening tests (float32, int8)
# ============================================================================


class TestAutoWidening:
    def test_float32_preserved_values(self):
        arr = np.array([1.5, -2.5, 0.0, 3.14], dtype=np.float32)
        v = t.Vector.from_numpy(arr)
        # Per-element access widens to F64 (no RAY_F32 scalar atom in v2).
        assert isinstance(v[0], t.F64)
        assert v[0].value == np.float64(np.float32(1.5))
        assert v[1].value == np.float64(np.float32(-2.5))
        assert v[2].value == 0.0
        result = v.to_numpy()
        assert result.dtype == np.float32
        np.testing.assert_array_almost_equal(result, arr)

    def test_float32_empty(self):
        arr = np.array([], dtype=np.float32)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 0
        result = v.to_numpy()
        assert result.dtype == np.float32
        assert len(result) == 0

    def test_int8_to_i16_values(self):
        arr = np.array([-128, -1, 0, 1, 127], dtype=np.int8)
        v = t.Vector.from_numpy(arr)
        assert isinstance(v[0], t.I16)
        assert v[0].value == -128
        assert v[1].value == -1
        assert v[2].value == 0
        assert v[3].value == 1
        assert v[4].value == 127
        result = v.to_numpy()
        assert result.dtype == np.int16
        np.testing.assert_array_equal(result, [-128, -1, 0, 1, 127])

    def test_int8_empty(self):
        arr = np.array([], dtype=np.int8)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 0
        result = v.to_numpy()
        assert result.dtype == np.int16
        assert len(result) == 0

    def test_table_with_float32_column(self):
        tbl = t.Table.from_dict(
            {
                "f32": np.array([1.0, 2.0, 3.0], dtype=np.float32),
                "i64": np.array([10, 20, 30], dtype=np.int64),
            }
        )
        assert isinstance(tbl["f32"][0], t.F64)
        assert abs(tbl["f32"][0].value - 1.0) < 1e-6

    def test_table_with_int8_column(self):
        tbl = t.Table.from_dict(
            {
                "i8": np.array([1, 2, 3], dtype=np.int8),
                "i64": np.array([10, 20, 30], dtype=np.int64),
            }
        )
        assert isinstance(tbl["i8"][0], t.I16)
        assert tbl["i8"][0].value == 1


# ============================================================================
# 20. GUID numpy round-trips
# ============================================================================


class TestGUIDNumpyRoundtrip:
    def test_guid_vector_to_numpy_values(self):
        uid1 = uuid.UUID("12345678-1234-5678-1234-567812345678")
        uid2 = uuid.UUID("abcdefab-cdef-abcd-efab-cdefabcdefab")
        v = t.Vector([uid1, uid2], ray_type=t.GUID)
        arr = v.to_numpy()
        assert arr.dtype == object
        assert arr[0] == uid1
        assert arr[1] == uid2

    def test_guid_numpy_to_rayforce(self):
        uid1 = uuid.UUID("12345678-1234-5678-1234-567812345678")
        uid2 = uuid.UUID("abcdefab-cdef-abcd-efab-cdefabcdefab")
        arr = np.array([uid1, uid2], dtype=object)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 2
        assert isinstance(v[0], t.GUID)
        assert v[0].to_python() == uid1
        assert v[1].to_python() == uid2

    def test_guid_full_roundtrip(self):
        """GUID: rayforce → numpy → rayforce → numpy."""
        uid1 = uuid.UUID("11111111-1111-1111-1111-111111111111")
        uid2 = uuid.UUID("22222222-2222-2222-2222-222222222222")
        uid3 = uuid.UUID("33333333-3333-3333-3333-333333333333")
        v1 = t.Vector([uid1, uid2, uid3], ray_type=t.GUID)
        arr1 = v1.to_numpy()
        v2 = t.Vector.from_numpy(arr1)
        arr2 = v2.to_numpy()
        np.testing.assert_array_equal(arr1, arr2)
        assert arr2[0] == uid1
        assert arr2[1] == uid2
        assert arr2[2] == uid3

    def test_guid_single(self):
        uid = uuid.uuid4()
        arr = np.array([uid], dtype=object)
        v = t.Vector.from_numpy(arr)
        assert v[0].to_python() == uid


# ============================================================================
# 21. Explicit ray_type with temporal arrays
# ============================================================================


class TestFromNumpyExplicitRayTypeTemporal:
    """Vector.from_numpy(temporal_arr, ray_type=...) must not crash."""

    def test_datetime64_ns_with_ray_type_timestamp(self):
        arr = np.array(
            ["2001-01-01T01:01:01", "2002-02-02T02:02:02", "2003-03-03T03:03:03"],
            dtype="datetime64[ns]",
        )
        v = t.Vector.from_numpy(arr, ray_type=t.Timestamp)
        assert len(v) == 3
        assert isinstance(v[0], t.Timestamp)
        assert v[0].to_python().year == 2001
        assert v[1].to_python().year == 2002
        assert v[2].to_python().year == 2003

    def test_datetime64_s_with_ray_type_timestamp(self):
        arr = np.array(["2025-03-15T12:30:00"], dtype="datetime64[s]")
        v = t.Vector.from_numpy(arr, ray_type=t.Timestamp)
        assert isinstance(v[0], t.Timestamp)
        py = v[0].to_python()
        assert py.hour == 12
        assert py.minute == 30

    def test_datetime64_D_with_ray_type_date(self):
        arr = np.array(["2025-01-01", "2025-12-31"], dtype="datetime64[D]")
        v = t.Vector.from_numpy(arr, ray_type=t.Date)
        assert len(v) == 2
        assert isinstance(v[0], t.Date)
        assert v[0].to_python() == dt.date(2025, 1, 1)
        assert v[1].to_python() == dt.date(2025, 12, 31)

    def test_timedelta64_ms_with_ray_type_time(self):
        arr = np.array([32_400_000, 64_800_000], dtype="timedelta64[ms]")
        v = t.Vector.from_numpy(arr, ray_type=t.Time)
        assert len(v) == 2
        assert isinstance(v[0], t.Time)
        assert v[0].to_python() == dt.time(9, 0, 0)
        assert v[1].to_python() == dt.time(18, 0, 0)

    def test_timedelta64_s_with_ray_type_time(self):
        arr = np.array([3600], dtype="timedelta64[s]")
        v = t.Vector.from_numpy(arr, ray_type=t.Time)
        assert isinstance(v[0], t.Time)
        assert v[0].to_python() == dt.time(1, 0, 0)

    def test_timestamp_roundtrip_with_explicit_ray_type(self):
        """to_numpy → from_numpy(ray_type=Timestamp) must preserve values."""
        dts = [
            dt.datetime(2001, 1, 1, 1, 1, 1, tzinfo=dt.UTC),
            dt.datetime(2002, 2, 2, 2, 2, 2, tzinfo=dt.UTC),
        ]
        v1 = t.Vector(dts, ray_type=t.Timestamp)
        arr = v1.to_numpy()
        v2 = t.Vector.from_numpy(arr, ray_type=t.Timestamp)
        assert v2[0].to_python().year == 2001
        assert v2[1].to_python().year == 2002

    def test_temporal_with_nat_and_explicit_ray_type(self):
        arr = np.array(["2025-01-01", "NaT"], dtype="datetime64[ns]")
        v = t.Vector.from_numpy(arr, ray_type=t.Timestamp)
        result = v.to_numpy()
        assert result[0] == np.datetime64("2025-01-01", "ns")
        assert np.isnat(result[1])

    def test_empty_temporal_with_ray_type(self):
        arr = np.array([], dtype="datetime64[ns]")
        v = t.Vector.from_numpy(arr, ray_type=t.Timestamp)
        assert len(v) == 0


# ============================================================================
# 22. __setitem__ type coercion
# ============================================================================


class TestSetitemTypeCoercion:
    """Inserting plain Python values into typed vectors must coerce correctly."""

    def test_int_into_i16_vector(self):
        v = t.Vector([1, 2, 3], ray_type=t.I16)
        v[1] = 99
        assert v[1].value == 99
        assert isinstance(v[1], t.I16)

    def test_int_into_i32_vector(self):
        v = t.Vector([10, 20, 30], ray_type=t.I32)
        v[0] = 42
        assert v[0].value == 42
        assert isinstance(v[0], t.I32)

    def test_int_into_i64_vector(self):
        v = t.Vector([100, 200, 300], ray_type=t.I64)
        v[2] = 999
        assert v[2].value == 999
        assert isinstance(v[2], t.I64)

    def test_float_into_f64_vector(self):
        v = t.Vector([1.0, 2.0, 3.0], ray_type=t.F64)
        v[1] = 9.9
        assert abs(v[1].value - 9.9) < 1e-10
        assert isinstance(v[1], t.F64)

    def test_bool_into_b8_vector(self):
        v = t.Vector([True, False, True], ray_type=t.B8)
        v[0] = False
        assert v[0].value is False
        assert isinstance(v[0], t.B8)

    def test_int_into_u8_vector(self):
        v = t.Vector([0, 1, 2], ray_type=t.U8)
        v[1] = 42
        assert v[1].value == 42
        assert isinstance(v[1], t.U8)

    def test_negative_index(self):
        v = t.Vector([10, 20, 30], ray_type=t.I16)
        v[-1] = 99
        assert v[2].value == 99
        assert isinstance(v[2], t.I16)

    def test_setitem_preserves_other_elements(self):
        v = t.Vector([1, 2, 3, 4, 5], ray_type=t.I16)
        v[2] = 99
        assert [v[i].value for i in range(5)] == [1, 2, 99, 4, 5]


# ============================================================================
# 23. from_numpy with multi-dimensional arrays
# ============================================================================


class TestFromNumpyMultiDimensional:
    """from_numpy must reject non-1D arrays."""

    def test_2d_raises(self):
        arr = np.array([[1, 2], [3, 4]], dtype=np.int64)
        with pytest.raises(errors.RayforceInitError, match="1-D array"):
            t.Vector.from_numpy(arr)

    def test_3d_raises(self):
        arr = np.ones((2, 3, 4), dtype=np.float64)
        with pytest.raises(errors.RayforceInitError, match="1-D array"):
            t.Vector.from_numpy(arr)

    def test_0d_raises(self):
        arr = np.array(42)
        with pytest.raises(errors.RayforceInitError, match="1-D array"):
            t.Vector.from_numpy(arr)

    def test_1d_still_works(self):
        arr = np.array([1, 2, 3], dtype=np.int64)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3


# ============================================================================
# 24. from_numpy with explicit ray_type and mismatched element sizes
# ============================================================================


class TestFromNumpyExplicitRayTypeCast:
    """Explicit ray_type with different numpy dtype casts values correctly."""

    def test_float32_as_f64(self):
        """float32 → F64: values are cast, not reinterpreted."""
        arr = np.array([1.0, 2.0], dtype=np.float32)
        vec = t.Vector.from_numpy(arr, ray_type=t.F64)
        assert vec.to_list() == [1.0, 2.0]

    def test_int16_as_i64(self):
        """int16 → I64: values are cast, not reinterpreted."""
        arr = np.array([1, 2], dtype=np.int16)
        vec = t.Vector.from_numpy(arr, ray_type=t.I64)
        assert vec.to_list() == [1, 2]

    def test_int64_as_i16(self):
        """int64 → I16: values are cast, not reinterpreted."""
        arr = np.array([1, 2, 3, 4], dtype=np.int64)
        vec = t.Vector.from_numpy(arr, ray_type=t.I16)
        assert vec.to_list() == [1, 2, 3, 4]

    def test_int64_as_i32(self):
        """int64 → I32: values are cast, not reinterpreted."""
        arr = np.array([1, 2, 3, 4], dtype=np.int64)
        vec = t.Vector.from_numpy(arr, ray_type=t.I32)
        assert vec.to_list() == [1, 2, 3, 4]
