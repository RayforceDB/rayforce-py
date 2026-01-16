import datetime as dt
import uuid

import pytest

from rayforce import errors
from rayforce import types as t


def test_vector():
    v = t.Vector(ray_type=t.Symbol, length=3)
    v[0] = "test1"
    v[1] = "test2"
    v[2] = "test3"

    assert len(v) == 3
    assert v[0].value == "test1"
    assert v[1].value == "test2"
    assert v[2].value == "test3"

    v2 = t.Vector(ray_type=t.I64, items=[100, 200, 300])
    assert len(v2) == 3
    assert v2[0].value == 100
    assert v2[1].value == 200
    assert v2[2].value == 300


class TestVectorTypeInference:
    def test_infer_int_to_i64(self):
        v = t.Vector([1, 2, 3])
        assert len(v) == 3
        assert isinstance(v[0], t.I64)
        assert v[0].value == 1

    def test_infer_float_to_f64(self):
        v = t.Vector([1.5, 2.5, 3.5])
        assert len(v) == 3
        assert isinstance(v[0], t.F64)
        assert v[0].value == 1.5

    def test_infer_bool_to_b8(self):
        v = t.Vector([True, False, True])
        assert len(v) == 3
        assert isinstance(v[0], t.B8)
        assert v[0].value is True

    def test_infer_str_to_symbol(self):
        v = t.Vector(["apple", "banana", "cherry"])
        assert len(v) == 3
        assert isinstance(v[0], t.Symbol)
        assert v[0].value == "apple"

    def test_infer_datetime_to_timestamp(self):
        dates = [dt.datetime(2025, 1, 1), dt.datetime(2025, 1, 2)]
        v = t.Vector(dates)
        assert len(v) == 2
        assert isinstance(v[0], t.Timestamp)

    def test_infer_date_to_date(self):
        dates = [dt.date(2025, 1, 1), dt.date(2025, 1, 2)]
        v = t.Vector(dates)
        assert len(v) == 2
        assert isinstance(v[0], t.Date)

    def test_infer_time_to_time(self):
        times = [dt.time(12, 30), dt.time(14, 45)]
        v = t.Vector(times)
        assert len(v) == 2
        assert isinstance(v[0], t.Time)

    def test_infer_uuid_to_guid(self):
        uuids = [uuid.uuid4(), uuid.uuid4()]
        v = t.Vector(uuids)
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
