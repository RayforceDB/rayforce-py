import datetime as dt
import uuid
import pytest
from raypy import _rayforce_c as r
from raypy.utils.conversion import python_to_ray, ray_to_python, RayConversionError
from raypy.types.operators import Operation
from raypy import types as t


def test_python_to_ray_bool():
    result = python_to_ray(True)
    assert isinstance(result, r.RayObject)
    assert t.B8(ptr=result).value == True

    result = python_to_ray(False)
    assert isinstance(result, r.RayObject)
    assert t.B8(ptr=result).value == False


def test_python_to_ray_int():
    result = python_to_ray(42)
    assert isinstance(result, r.RayObject)
    assert t.I64(ptr=result).value == 42


def test_python_to_ray_float():
    result = python_to_ray(123.45)
    assert isinstance(result, r.RayObject)
    assert t.F64(ptr=result).value == 123.45


def test_python_to_ray_datetime():
    dt_obj = dt.datetime(2025, 5, 10, 14, 30, 45, tzinfo=dt.timezone.utc)
    result = python_to_ray(dt_obj)
    assert isinstance(result, r.RayObject)
    assert isinstance(t.Timestamp(ptr=result).value, dt.datetime)


def test_python_to_ray_date():
    date_obj = dt.date(2025, 5, 10)
    result = python_to_ray(date_obj)
    assert isinstance(result, r.RayObject)
    assert t.Date(ptr=result).value == date_obj


def test_python_to_ray_time():
    time_obj = dt.time(14, 30, 45)
    result = python_to_ray(time_obj)
    assert isinstance(result, r.RayObject)
    assert t.Time(ptr=result).value == time_obj


def test_python_to_ray_uuid():
    u_id = uuid.uuid4()
    result = python_to_ray(u_id)
    assert isinstance(result, r.RayObject)
    assert t.GUID(ptr=result).value == u_id


def test_python_to_ray_str():
    result = python_to_ray("test")
    assert isinstance(result, r.RayObject)
    assert t.Symbol(ptr=result).value == "test"


def test_python_to_ray_dict():
    result = python_to_ray({"key": 123})
    assert isinstance(result, r.RayObject)
    assert isinstance(t.Dict(ptr=result), t.Dict)


def test_python_to_ray_list():
    result = python_to_ray([1, 2, 3])
    assert isinstance(result, r.RayObject)
    assert isinstance(t.List(ptr=result), t.List)


def test_python_to_ray_tuple():
    result = python_to_ray((1, 2, 3))
    assert isinstance(result, r.RayObject)
    assert isinstance(t.List(ptr=result), t.List)


def test_python_to_ray_none():
    result = python_to_ray(None)
    assert isinstance(result, r.RayObject)
    assert isinstance(t.List(ptr=result), t.List)


def test_python_to_ray_rayobject_wrapper():
    i16_obj = t.I16(42)
    result = python_to_ray(i16_obj)
    assert result == i16_obj.ptr


def test_python_to_ray_operation():
    result = python_to_ray(Operation.ADD)
    assert isinstance(result, r.RayObject)


def test_python_to_ray_rayobject_direct():
    i16_obj = t.I16(42)
    result = python_to_ray(i16_obj.ptr)
    assert result == i16_obj.ptr


def test_python_to_ray_unsupported():
    with pytest.raises(RayConversionError):
        python_to_ray(object())


def test_ray_to_python_scalar():
    i16_obj = t.I16(42)
    result = ray_to_python(i16_obj.ptr)
    assert isinstance(result, t.I16)
    assert result.value == 42


def test_ray_to_python_container():
    list_obj = t.List([1, 2, 3])
    result = ray_to_python(list_obj.ptr)
    assert isinstance(result, t.List)


def test_ray_to_python_invalid():
    with pytest.raises(RayConversionError, match="Expected RayObject"):
        ray_to_python("not a RayObject")
