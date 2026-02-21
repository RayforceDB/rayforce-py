import datetime as dt
import uuid

import numpy as np
import pytest

from rayforce import errors
from rayforce import types as t


def test_vector_with_ray_type_and_length():
    v = t.Vector(ray_type=t.Symbol, length=3)
    v[0] = "test1"
    v[1] = "test2"
    v[2] = "test3"

    assert len(v) == 3
    assert v[0].value == "test1"
    assert v[1].value == "test2"
    assert v[2].value == "test3"


def test_vector_with_items():
    v = t.Vector(ray_type=t.I64, items=[100, 200, 300])
    assert len(v) == 3
    assert v[0].value == 100
    assert v[1].value == 200
    assert v[2].value == 300


class TestVectorTypeInference:
    @pytest.mark.parametrize(
        "items,expected_type,check_val",
        [
            ([1, 2, 3], t.I64, 1),
            ([1.5, 2.5, 3.5], t.F64, 1.5),
            ([True, False, True], t.B8, True),
            (["apple", "banana", "cherry"], t.Symbol, "apple"),
        ],
    )
    def test_infer_primitive_types(self, items, expected_type, check_val):
        v = t.Vector(items)
        assert len(v) == len(items)
        assert isinstance(v[0], expected_type)
        assert v[0].value == check_val

    def test_infer_datetime_to_timestamp(self):
        v = t.Vector([dt.datetime(2025, 1, 1), dt.datetime(2025, 1, 2)])
        assert len(v) == 2
        assert isinstance(v[0], t.Timestamp)

    def test_infer_date_to_date(self):
        v = t.Vector([dt.date(2025, 1, 1), dt.date(2025, 1, 2)])
        assert len(v) == 2
        assert isinstance(v[0], t.Date)

    def test_infer_time_to_time(self):
        v = t.Vector([dt.time(12, 30), dt.time(14, 45)])
        assert len(v) == 2
        assert isinstance(v[0], t.Time)

    def test_infer_uuid_to_guid(self):
        v = t.Vector([uuid.uuid4(), uuid.uuid4()])
        assert len(v) == 2
        assert isinstance(v[0], t.GUID)

    def test_explicit_ray_type_overrides_inference(self):
        v = t.Vector([1, 2, 3], ray_type=t.F64)
        assert len(v) == 3
        assert isinstance(v[0], t.F64)
        assert v[0].value == 1.0

    def test_empty_items_raises_error(self):
        with pytest.raises(errors.RayforceInitError, match="Cannot infer vector"):
            t.Vector([])

    def test_none_items_creates_null_vector(self):
        v = t.Vector([None, None, None])
        assert len(v) == 3


class TestVectorNegativeIndexing:
    def test_negative_index_last_element(self):
        v = t.Vector([10, 20, 30])
        assert v[-1].value == 30

    def test_negative_index_first_element(self):
        v = t.Vector([10, 20, 30])
        assert v[-3].value == 10

    def test_negative_index_middle_element(self):
        v = t.Vector([10, 20, 30])
        assert v[-2].value == 20

    def test_negative_index_out_of_range(self):
        v = t.Vector([10, 20, 30])
        with pytest.raises(errors.RayforceIndexError, match="out of range"):
            v[-4]

    def test_negative_index_setitem(self):
        v = t.Vector([10, 20, 30], ray_type=t.I64)
        v[-1] = 99
        assert v[2].value == 99


class TestVectorSingleElement:
    def test_single_int_element(self):
        v = t.Vector([42])
        assert len(v) == 1
        assert v[0].value == 42

    def test_single_string_element(self):
        v = t.Vector(["only"])
        assert len(v) == 1
        assert v[0].value == "only"

    def test_single_element_negative_index(self):
        v = t.Vector([42])
        assert v[-1].value == 42


class TestVectorIteration:
    def test_for_loop_collects_all_elements(self):
        v = t.Vector([10, 20, 30])
        values = [item.value for item in v]
        assert values == [10, 20, 30]

    def test_iteration_empty_with_type(self):
        v = t.Vector(ray_type=t.I64, length=0)
        values = list(v)
        assert values == []

    def test_to_python_returns_list(self):
        v = t.Vector([1, 2, 3])
        result = v.to_python()
        assert isinstance(result, list)
        assert len(result) == 3


class TestVectorEquality:
    def test_equal_vectors(self):
        v1 = t.Vector([1, 2, 3])
        v2 = t.Vector([1, 2, 3])
        assert v1 == v2

    def test_unequal_vectors(self):
        v1 = t.Vector([1, 2, 3])
        v2 = t.Vector([4, 5, 6])
        assert v1 != v2

    def test_vector_equals_python_list(self):
        v = t.Vector([1, 2, 3])
        assert v == v.to_python()


class TestVectorMixedTypeRejection:
    def test_mixed_int_and_string_raises(self):
        with pytest.raises(Exception):
            t.Vector([1, "two", 3])

    def test_mixed_int_and_float_coerced(self):
        # ints can coerce to float with explicit ray_type
        v = t.Vector([1, 2, 3], ray_type=t.F64)
        assert v[0].value == 1.0


class TestVectorLarge:
    def test_large_vector_creation(self):
        items = list(range(10_000))
        v = t.Vector(items)
        assert len(v) == 10_000
        assert v[0].value == 0
        assert v[9999].value == 9999

    def test_large_vector_negative_index(self):
        items = list(range(10_000))
        v = t.Vector(items)
        assert v[-1].value == 9999


class TestVectorToList:
    def test_i64(self):
        v = t.Vector([10, 20, 30], ray_type=t.I64)
        assert v.to_list() == [10, 20, 30]

    def test_f64(self):
        v = t.Vector([1.5, 2.5, 3.5], ray_type=t.F64)
        assert v.to_list() == [1.5, 2.5, 3.5]

    def test_u8(self):
        v = t.Vector([1, 2, 255], ray_type=t.U8)
        assert v.to_list() == [1, 2, 255]

    def test_b8(self):
        v = t.Vector([True, False, True], ray_type=t.B8)
        result = v.to_list()
        assert result == [1, 0, 1]

    def test_i16(self):
        v = t.Vector([100, -200, 300], ray_type=t.I16)
        assert v.to_list() == [100, -200, 300]

    def test_i32(self):
        v = t.Vector([100000, -200000, 300000], ray_type=t.I32)
        assert v.to_list() == [100000, -200000, 300000]

    def test_symbol_fallback(self):
        v = t.Vector(["alice", "bob"], ray_type=t.Symbol)
        assert v.to_list() == ["alice", "bob"]

    def test_date(self):
        v = t.Vector([dt.date(2025, 1, 1), dt.date(2025, 6, 15)], ray_type=t.Date)
        result = v.to_list()
        assert len(result) == 2
        assert all(isinstance(x, int) for x in result)

    def test_timestamp(self):
        v = t.Vector(
            [
                dt.datetime(2025, 1, 1, tzinfo=dt.UTC),
                dt.datetime(2025, 6, 15, tzinfo=dt.UTC),
            ],
            ray_type=t.Timestamp,
        )
        result = v.to_list()
        assert len(result) == 2
        assert all(isinstance(x, int) for x in result)

    def test_empty_vector(self):
        v = t.Vector(ray_type=t.I64, length=0)
        assert v.to_list() == []

    def test_single_element(self):
        v = t.Vector([42], ray_type=t.I64)
        assert v.to_list() == [42]

    def test_large_vector(self):
        items = list(range(100_000))
        v = t.Vector(items, ray_type=t.I64)
        result = v.to_list()
        assert result == items


class TestVectorToNumpy:
    def test_i64(self):
        v = t.Vector([10, 20, 30], ray_type=t.I64)
        arr = v.to_numpy()
        np.testing.assert_array_equal(arr, [10, 20, 30])
        assert arr.dtype == np.int64

    def test_f64(self):
        v = t.Vector([1.5, 2.5, 3.5], ray_type=t.F64)
        arr = v.to_numpy()
        np.testing.assert_array_equal(arr, [1.5, 2.5, 3.5])
        assert arr.dtype == np.float64

    def test_u8(self):
        v = t.Vector([1, 2, 255], ray_type=t.U8)
        arr = v.to_numpy()
        np.testing.assert_array_equal(arr, [1, 2, 255])
        assert arr.dtype == np.uint8

    def test_b8(self):
        v = t.Vector([True, False, True], ray_type=t.B8)
        arr = v.to_numpy()
        assert arr.dtype == np.bool_
        np.testing.assert_array_equal(arr, [True, False, True])

    def test_i16(self):
        v = t.Vector([100, -200, 300], ray_type=t.I16)
        arr = v.to_numpy()
        np.testing.assert_array_equal(arr, [100, -200, 300])
        assert arr.dtype == np.int16

    def test_i32(self):
        v = t.Vector([100000, -200000, 300000], ray_type=t.I32)
        arr = v.to_numpy()
        np.testing.assert_array_equal(arr, [100000, -200000, 300000])
        assert arr.dtype == np.int32

    def test_symbol_fallback(self):
        v = t.Vector(["alice", "bob"], ray_type=t.Symbol)
        arr = v.to_numpy()
        np.testing.assert_array_equal(arr, ["alice", "bob"])

    def test_empty_vector(self):
        v = t.Vector(ray_type=t.I64, length=0)
        arr = v.to_numpy()
        assert len(arr) == 0
        assert arr.dtype == np.int64

    def test_large_vector(self):
        items = list(range(100_000))
        v = t.Vector(items, ray_type=t.I64)
        arr = v.to_numpy()
        np.testing.assert_array_equal(arr, items)

    def test_single_element(self):
        v = t.Vector([42], ray_type=t.I64)
        arr = v.to_numpy()
        np.testing.assert_array_equal(arr, [42])
        assert arr.shape == (1,)

    def test_f64_negative_values(self):
        v = t.Vector([-1.5, 0.0, 1.5], ray_type=t.F64)
        arr = v.to_numpy()
        np.testing.assert_array_equal(arr, [-1.5, 0.0, 1.5])

    def test_i64_negative_values(self):
        v = t.Vector([-100, 0, 100], ray_type=t.I64)
        arr = v.to_numpy()
        np.testing.assert_array_equal(arr, [-100, 0, 100])

    def test_date_returns_datetime64(self):
        v = t.Vector([dt.date(2025, 1, 1), dt.date(2025, 6, 15)], ray_type=t.Date)
        arr = v.to_numpy()
        assert arr.dtype == "datetime64[D]"
        assert arr.shape == (2,)
        assert arr[0] == np.datetime64("2025-01-01")
        assert arr[1] == np.datetime64("2025-06-15")

    def test_timestamp_returns_datetime64(self):
        v = t.Vector(
            [
                dt.datetime(2025, 1, 1, tzinfo=dt.UTC),
                dt.datetime(2025, 6, 15, 12, 0, 0, tzinfo=dt.UTC),
            ],
            ray_type=t.Timestamp,
        )
        arr = v.to_numpy()
        assert arr.dtype == "datetime64[ns]"
        assert arr.shape == (2,)
        assert arr[0] == np.datetime64("2025-01-01T00:00:00", "ns")
        assert arr[1] == np.datetime64("2025-06-15T12:00:00", "ns")

    def test_numpy_array_is_usable_in_operations(self):
        v = t.Vector([10, 20, 30], ray_type=t.F64)
        arr = v.to_numpy()
        result = arr * 2 + 1
        np.testing.assert_array_equal(result, [21.0, 41.0, 61.0])

    def test_numpy_array_supports_aggregation(self):
        v = t.Vector([10, 20, 30, 40, 50], ray_type=t.I64)
        arr = v.to_numpy()
        assert arr.sum() == 150
        assert arr.mean() == 30.0
        assert arr.min() == 10
        assert arr.max() == 50

    def test_to_list_matches_to_numpy_for_numeric(self):
        v = t.Vector([1.1, 2.2, 3.3], ray_type=t.F64)
        lst = v.to_list()
        arr = v.to_numpy()
        np.testing.assert_array_almost_equal(arr, lst)


class TestVectorToNumpyLarge:
    """Tests with 1M+ element vectors to verify bulk memcpy at scale."""

    N = 1_000_000

    def test_i64_1m(self):
        v = t.Vector(list(range(self.N)), ray_type=t.I64)
        arr = v.to_numpy()
        assert arr.shape == (self.N,)
        assert arr.dtype == np.int64
        assert arr[0] == 0
        assert arr[-1] == self.N - 1
        assert arr.sum() == (self.N - 1) * self.N // 2

    def test_f64_1m(self):
        v = t.Vector([float(i) for i in range(self.N)], ray_type=t.F64)
        arr = v.to_numpy()
        assert arr.shape == (self.N,)
        assert arr.dtype == np.float64
        assert arr[0] == 0.0
        assert arr[-1] == float(self.N - 1)

    def test_i32_1m(self):
        v = t.Vector(list(range(self.N)), ray_type=t.I32)
        arr = v.to_numpy()
        assert arr.shape == (self.N,)
        assert arr.dtype == np.int32
        assert arr[0] == 0
        assert arr[-1] == self.N - 1

    def test_u8_1m(self):
        items = [i % 256 for i in range(self.N)]
        v = t.Vector(items, ray_type=t.U8)
        arr = v.to_numpy()
        assert arr.shape == (self.N,)
        assert arr.dtype == np.uint8
        assert arr[0] == 0
        assert arr[255] == 255
        assert arr[256] == 0

    def test_to_list_matches_to_numpy_1m(self):
        v = t.Vector(list(range(self.N)), ray_type=t.I64)
        lst = v.to_list()
        arr = v.to_numpy()
        np.testing.assert_array_equal(arr, lst)


class TestVectorFromNumpy:
    def test_i64(self):
        arr = np.array([10, 20, 30], dtype=np.int64)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert v[0].value == 10
        assert v[1].value == 20
        assert v[2].value == 30

    def test_f64(self):
        arr = np.array([1.5, 2.5, 3.5], dtype=np.float64)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert v[0].value == 1.5
        assert v[2].value == 3.5

    def test_i32(self):
        arr = np.array([100, -200, 300], dtype=np.int32)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert v[0].value == 100
        assert v[1].value == -200

    def test_i16(self):
        arr = np.array([10, 20, 30], dtype=np.int16)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert v[0].value == 10

    def test_u8(self):
        arr = np.array([0, 128, 255], dtype=np.uint8)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert v.to_list() == [0, 128, 255]

    def test_bool(self):
        arr = np.array([True, False, True], dtype=np.bool_)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert v[0].value is True
        assert v[1].value is False

    def test_explicit_ray_type(self):
        arr = np.array([1, 2, 3], dtype=np.int64)
        v = t.Vector.from_numpy(arr, ray_type=t.F64)
        assert len(v) == 3
        assert isinstance(v[0], t.F64)

    def test_empty_array(self):
        arr = np.array([], dtype=np.int64)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 0

    def test_single_element(self):
        arr = np.array([42], dtype=np.int64)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 1
        assert v[0].value == 42

    def test_roundtrip_i64(self):
        original = np.array([10, 20, 30, 40, 50], dtype=np.int64)
        v = t.Vector.from_numpy(original)
        result = v.to_numpy()
        np.testing.assert_array_equal(result, original)

    def test_roundtrip_f64(self):
        original = np.array([1.1, 2.2, 3.3], dtype=np.float64)
        v = t.Vector.from_numpy(original)
        result = v.to_numpy()
        np.testing.assert_array_almost_equal(result, original)

    def test_large_1m(self):
        arr = np.arange(1_000_000, dtype=np.int64)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 1_000_000
        assert v[0].value == 0
        assert v[-1].value == 999_999
        result = v.to_numpy()
        np.testing.assert_array_equal(result, arr)

    def test_negative_values(self):
        arr = np.array([-100, 0, 100], dtype=np.int64)
        v = t.Vector.from_numpy(arr)
        assert v[0].value == -100
        assert v[1].value == 0
        assert v[2].value == 100

    def test_symbol_from_object_array(self):
        arr = np.array(["alice", "bob", "charlie"], dtype=object)
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert v[0].value == "alice"
        assert v[1].value == "bob"
        assert v[2].value == "charlie"

    def test_symbol_from_unicode_array(self):
        arr = np.array(["apple", "banana", "cherry"])
        v = t.Vector.from_numpy(arr)
        assert len(v) == 3
        assert v[0].value == "apple"
        assert v[2].value == "cherry"

    def test_symbol_roundtrip(self):
        arr = np.array(["x", "y", "z"])
        v = t.Vector.from_numpy(arr)
        result = v.to_list()
        assert result == ["x", "y", "z"]

    def test_timestamp_from_datetime64_ns(self):
        arr = np.array(["2025-01-01", "2025-06-15"], dtype="datetime64[ns]")
        v = t.Vector.from_numpy(arr)
        assert len(v) == 2
        assert isinstance(v[0], t.Timestamp)
        assert v[0].to_python().year == 2025
        assert v[0].to_python().month == 1
        assert v[0].to_python().day == 1
        assert v[1].to_python().month == 6

    def test_timestamp_from_datetime64_s(self):
        arr = np.array(["2025-03-15T12:30:00", "2025-07-20T18:00:00"], dtype="datetime64[s]")
        v = t.Vector.from_numpy(arr)
        assert len(v) == 2
        assert isinstance(v[0], t.Timestamp)
        assert v[0].to_python().hour == 12
        assert v[0].to_python().minute == 30

    def test_timestamp_roundtrip(self):
        dates = [dt.datetime(2025, 1, 1), dt.datetime(2025, 6, 15, 12, 0, 0)]
        arr = np.array(dates, dtype="datetime64[ns]")
        v = t.Vector.from_numpy(arr)
        assert v[0].to_python().replace(tzinfo=None) == dates[0]
        assert v[1].to_python().replace(tzinfo=None) == dates[1]

    def test_date_from_datetime64_D(self):
        arr = np.array(["2025-01-01", "2025-12-31"], dtype="datetime64[D]")
        v = t.Vector.from_numpy(arr)
        assert len(v) == 2
        assert isinstance(v[0], t.Date)
        assert v[0].to_python() == dt.date(2025, 1, 1)
        assert v[1].to_python() == dt.date(2025, 12, 31)

    def test_date_roundtrip(self):
        dates = [dt.date(2025, 1, 1), dt.date(2025, 6, 15)]
        v1 = t.Vector(dates, ray_type=t.Date)
        arr = np.array(dates, dtype="datetime64[D]")
        v2 = t.Vector.from_numpy(arr)
        assert v1[0].to_python() == v2[0].to_python()
        assert v1[1].to_python() == v2[1].to_python()

    def test_time_from_timedelta64(self):
        # 12:30:00 = 45_000_000 ms, 18:00:00 = 64_800_000 ms
        arr = np.array([45_000_000, 64_800_000], dtype="timedelta64[ms]")
        v = t.Vector.from_numpy(arr)
        assert len(v) == 2
        assert isinstance(v[0], t.Time)
        assert v[0].to_python() == dt.time(12, 30, 0)
        assert v[1].to_python() == dt.time(18, 0, 0)

    def test_time_roundtrip(self):
        times = [dt.time(9, 30, 0), dt.time(14, 45, 30)]
        v1 = t.Vector(times, ray_type=t.Time)
        ms_values = [v1[0].to_millis(), v1[1].to_millis()]
        arr = np.array(ms_values, dtype="timedelta64[ms]")
        v2 = t.Vector.from_numpy(arr)
        assert v1[0].to_python() == v2[0].to_python()
        assert v1[1].to_python() == v2[1].to_python()

    def test_unsupported_dtype_raises(self):
        arr = np.array([1 + 2j, 3 + 4j], dtype=np.complex128)
        with pytest.raises(errors.RayforceInitError, match="Cannot infer ray_type"):
            t.Vector.from_numpy(arr)

    def test_not_ndarray_raises(self):
        with pytest.raises(errors.RayforceInitError, match="requires a numpy ndarray"):
            t.Vector.from_numpy([1, 2, 3])
