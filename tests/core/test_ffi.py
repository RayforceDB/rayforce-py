import pytest
import threading
from rayforce.ffi import FFI
from rayforce import _rayforce_c as r
from rayforce.errors import RayforceThreadError


@pytest.mark.parametrize(
    "func,success_arg,fail_arg",
    [
        (FFI.init_i16, 42, "invalid"),
        (FFI.init_i32, 100, "invalid"),
        (FFI.init_i64, 1000, "invalid"),
        (FFI.init_f64, 3.14, "invalid"),
        (FFI.init_u8, 255, "invalid"),
        # init_b8 accepts any python object
        (FFI.init_c8, "a", "invalid"),
        (FFI.init_symbol, "test", None),
        (FFI.init_date, 0, "invalid"),
        (FFI.init_time, 0, "invalid"),
        (FFI.init_timestamp, 0, "invalid"),
        (FFI.init_guid, "00000000-0000-0000-0000-000000000000", "invalid"),
        (FFI.init_string, "hello", None),
    ],
)
def test_init_functions(func, success_arg, fail_arg):
    # Success case
    result = func(success_arg)
    assert isinstance(result, r.RayObject)

    # Failure case
    with pytest.raises(Exception):
        func(fail_arg)


@pytest.mark.parametrize(
    "init_func,read_func,value",
    [
        (FFI.init_i16, FFI.read_i16, 42),
        (FFI.init_i32, FFI.read_i32, 100),
        (FFI.init_i64, FFI.read_i64, 1000),
        (FFI.init_f64, FFI.read_f64, 3.14),
        (FFI.init_u8, FFI.read_u8, 255),
        (FFI.init_b8, FFI.read_b8, True),
        (FFI.init_c8, FFI.read_c8, "a"),
        (FFI.init_symbol, FFI.read_symbol, "test"),
    ],
)
def test_read_functions(init_func, read_func, value):
    # Success case
    obj = init_func(value)
    result = read_func(obj)
    assert result == value

    # Failure case
    wrong_obj = FFI.init_i32(42) if init_func != FFI.init_i32 else FFI.init_i64(42)
    with pytest.raises(Exception):
        read_func(wrong_obj)


@pytest.mark.parametrize(
    "init_func,read_func,value",
    [
        (FFI.init_date, FFI.read_date, 0),
        (FFI.init_time, FFI.read_time, 0),
        (FFI.init_timestamp, FFI.read_timestamp, 0),
        (FFI.init_guid, FFI.read_guid, "00000000-0000-0000-0000-000000000000"),
    ],
)
def test_read_complex_functions(init_func, read_func, value):
    # Success case
    obj = init_func(value)
    result = read_func(obj)
    assert result is not None

    # Failure case - wrong type
    wrong_obj = FFI.init_i32(42)
    with pytest.raises(Exception):
        read_func(wrong_obj)


def test_init_vector():
    # Success case
    vec = FFI.init_vector(r.TYPE_I64, 5)
    assert isinstance(vec, r.RayObject)
    assert FFI.get_obj_length(vec) == 5


def test_init_list():
    # Success case
    lst = FFI.init_list()
    assert isinstance(lst, r.RayObject)
    assert FFI.get_obj_length(lst) == 0


def test_init_dict():
    keys = FFI.init_vector(r.TYPE_SYMBOL, 2)
    values = FFI.init_list()
    FFI.push_obj(values, FFI.init_i32(1))
    FFI.push_obj(values, FFI.init_i32(2))

    # Success case
    dct = FFI.init_dict(keys, values)
    assert isinstance(dct, r.RayObject)

    # Failure case - mismatched lengths
    keys2 = FFI.init_vector(r.TYPE_SYMBOL, 1)
    with pytest.raises(Exception):
        FFI.init_dict(keys2, values)


def test_init_table():
    columns = FFI.init_vector(r.TYPE_SYMBOL, 2)
    values = FFI.init_list()
    col1_vals = FFI.init_vector(r.TYPE_I64, 2)
    col2_vals = FFI.init_vector(r.TYPE_I64, 2)
    FFI.push_obj(values, col1_vals)
    FFI.push_obj(values, col2_vals)

    # Success case
    table = FFI.init_table(columns, values)
    assert isinstance(table, r.RayObject)

    # Failure case - mismatched lengths
    columns2 = FFI.init_vector(r.TYPE_SYMBOL, 1)
    with pytest.raises(Exception):
        FFI.init_table(columns2, values)


def test_push_obj():
    # Success case
    lst = FFI.init_list()
    val = FFI.init_i32(42)
    FFI.push_obj(lst, val)
    assert FFI.get_obj_length(lst) == 1


def test_insert_obj():
    # Success case
    vec = FFI.init_vector(r.TYPE_I64, 3)
    val = FFI.init_i64(42)
    FFI.insert_obj(vec, 1, val)
    assert FFI.get_obj_length(vec) == 3


def test_at_idx():
    # Success case
    vec = FFI.init_vector(r.TYPE_I64, 3)
    result = FFI.at_idx(vec, 0)
    assert isinstance(result, r.RayObject)


def test_get_obj_length():
    # Success case
    vec = FFI.init_vector(r.TYPE_I64, 5)
    assert FFI.get_obj_length(vec) == 5


def test_get_table_keys():
    columns = FFI.init_vector(r.TYPE_SYMBOL, 2)
    values = FFI.init_list()
    col1_vals = FFI.init_vector(r.TYPE_I64, 2)
    col2_vals = FFI.init_vector(r.TYPE_I64, 2)
    FFI.push_obj(values, col1_vals)
    FFI.push_obj(values, col2_vals)

    # Success case
    table = FFI.init_table(columns, values)
    keys = FFI.get_table_keys(table)
    assert isinstance(keys, r.RayObject)


def test_get_table_values():
    columns = FFI.init_vector(r.TYPE_SYMBOL, 2)
    values = FFI.init_list()
    col1_vals = FFI.init_vector(r.TYPE_I64, 2)
    col2_vals = FFI.init_vector(r.TYPE_I64, 2)
    FFI.push_obj(values, col1_vals)
    FFI.push_obj(values, col2_vals)

    # Success case
    table = FFI.init_table(columns, values)
    vals = FFI.get_table_values(table)
    assert isinstance(vals, r.RayObject)


def test_dict_get():
    keys = FFI.init_vector(r.TYPE_SYMBOL, 1)
    values = FFI.init_list()
    FFI.push_obj(values, FFI.init_i32(42))
    dct = FFI.init_dict(keys, values)
    key = FFI.init_symbol("test")

    # Success case
    result = FFI.dict_get(dct, key)
    assert isinstance(result, r.RayObject)


def test_get_dict_keys():
    keys = FFI.init_vector(r.TYPE_SYMBOL, 1)
    values = FFI.init_list()
    FFI.push_obj(values, FFI.init_i32(42))
    dct = FFI.init_dict(keys, values)

    # Success case
    result = FFI.get_dict_keys(dct)
    assert isinstance(result, r.RayObject)


def test_get_dict_values():
    keys = FFI.init_vector(r.TYPE_SYMBOL, 1)
    values = FFI.init_list()
    FFI.push_obj(values, FFI.init_i32(42))
    dct = FFI.init_dict(keys, values)

    # Success case
    result = FFI.get_dict_values(dct)
    assert isinstance(result, r.RayObject)


def test_eval_str():
    # Success case
    expr = FFI.init_string("1")
    result = FFI.eval_str(expr)
    assert isinstance(result, r.RayObject)

    # Failure case - invalid expression
    invalid_expr = FFI.init_string("invalid_expr_!!!")
    with pytest.raises(Exception):
        FFI.eval_str(invalid_expr)


def test_eval_obj():
    # Success case
    obj = FFI.init_i32(42)
    result = FFI.eval_obj(obj)
    assert isinstance(result, r.RayObject)


def test_quote():
    # Success case
    obj = FFI.init_i32(42)
    result = FFI.quote(obj)
    assert isinstance(result, r.RayObject)

    # Failure case - invalid object
    with pytest.raises(Exception):
        FFI.quote(None)


def test_rc_obj():
    # Success case
    obj = FFI.init_i32(42)
    rc = FFI.rc_obj(obj)
    assert isinstance(rc, int)
    assert rc >= 0

    # Failure case - invalid object
    with pytest.raises(Exception):
        FFI.rc_obj(None)


def test_binary_set():
    # Success case
    name = FFI.init_symbol("test_var")
    value = FFI.init_i32(42)
    FFI.binary_set(name, value)

    # Failure case - invalid name
    with pytest.raises(Exception):
        FFI.binary_set(FFI.init_i32(42), value)


def test_env_get_internal_function_by_name():
    # Success case
    result = FFI.env_get_internal_function_by_name("+")
    assert result is None or isinstance(result, r.RayObject)

    # Failure case - invalid function name
    assert FFI.env_get_internal_function_by_name("ssssss") is None


def test_env_get_internal_name_by_function():
    # Success case - get function first
    func = FFI.env_get_internal_function_by_name("+")
    if func is not None:
        name = FFI.env_get_internal_name_by_function(func)
        assert isinstance(name, str)

    # Failure case - invalid function
    assert FFI.env_get_internal_name_by_function(FFI.init_i32(222222)) == "@fn"


def test_set_obj_attrs():
    # Success case
    obj = FFI.init_i32(42)
    FFI.set_obj_attrs(obj, 0)


def test_hopen():
    # Success case
    path = FFI.init_string("/dev/null")
    result = FFI.hopen(path)
    assert isinstance(result, r.RayObject)

    # Failure case - invalid path
    invalid_path = FFI.init_i32(42)
    with pytest.raises(Exception):
        FFI.hopen(invalid_path)


def test_hclose():
    # Success case
    handle = FFI.hopen(FFI.init_string("/dev/null"))
    FFI.hclose(handle)


def test_write():
    # Success case
    handle = FFI.hopen(FFI.init_string("/dev/null"))
    data = FFI.init_string("test")
    FFI.write(handle, data)
    FFI.hclose(handle)
    # No exception means success


def test_thread_safety():
    exception_raised = threading.Event()
    exception_type = None
    exception_message = None

    def worker_thread():
        nonlocal exception_type, exception_message
        try:
            FFI.init_i32(42)
        except RayforceThreadError as e:
            exception_type = type(e)
            exception_message = str(e)
            exception_raised.set()
        except Exception as e:
            exception_type = type(e)
            exception_message = str(e)
            exception_raised.set()

    thread = threading.Thread(target=worker_thread)
    thread.start()
    thread.join(timeout=5.0)

    assert exception_raised.is_set(), "Exception should have been raised"
    assert exception_type == RuntimeError, f"Expected RayforceThreadError, got {exception_type}"
    assert (
        exception_message
        == "Rayforce runtime can not be called from other threads than the one where it was initialized from"
    )
