import datetime as dt
import uuid

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
