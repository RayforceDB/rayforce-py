import threading

import pytest

from rayforce import _rayforce_c as r
from rayforce.errors import RayforceError, RayforceLengthError, RayforceThreadError
from rayforce.ffi import FFI

pytestmark = pytest.mark.ffi


@pytest.mark.parametrize(
    "func,success_arg,fail_arg",
    [
        (FFI.init_i16, 42, "invalid"),
        (FFI.init_i32, 100, "invalid"),
        (FFI.init_i64, 1000, "invalid"),
        (FFI.init_f64, 3.14, "invalid"),
        (FFI.init_u8, 255, "invalid"),
        # init_b8 accepts any python object
        (FFI.init_symbol, "test", None),
        (FFI.init_date, "2025-10-10", "invalid"),
        (FFI.init_time, "08:00:01", "invalid"),
        (FFI.init_timestamp, "2025-10-10 08:00:01.000111", "invalid"),
        (FFI.init_guid, "00000000-0000-0000-0000-000000000000", "invalid"),
        (FFI.init_string, "hello", None),
    ],
)
def test_init_functions(func, success_arg, fail_arg):
    result = func(success_arg)
    assert isinstance(result, r.RayObject)

    with pytest.raises((TypeError, RuntimeError, RayforceError)):
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
        (FFI.init_symbol, FFI.read_symbol, "test"),
    ],
)
def test_read_functions(init_func, read_func, value):
    obj = init_func(value)
    assert read_func(obj) == value

    wrong_obj = FFI.init_i32(42) if init_func != FFI.init_i32 else FFI.init_i64(42)
    with pytest.raises((RuntimeError, RayforceError)):
        read_func(wrong_obj)


@pytest.mark.parametrize(
    "init_func,read_func,value",
    [
        (FFI.init_date, FFI.read_date, "2025-10-10"),
        (FFI.init_time, FFI.read_time, "08:00:01"),
        (FFI.init_timestamp, FFI.read_timestamp, "2025-10-10 08:00:01.000111"),
        (FFI.init_guid, FFI.read_guid, "00000000-0000-0000-0000-000000000000"),
    ],
)
def test_read_complex_functions(init_func, read_func, value):
    obj = init_func(value)
    assert read_func(obj) is not None

    wrong_obj = FFI.init_i32(42)
    with pytest.raises((RuntimeError, RayforceError)):
        read_func(wrong_obj)


def test_init_vector():
    vec = FFI.init_vector(r.TYPE_I64, 5)
    assert isinstance(vec, r.RayObject)
    assert FFI.get_obj_length(vec) == 5


def test_init_list():
    lst = FFI.init_list([])
    assert isinstance(lst, r.RayObject)
    assert FFI.get_obj_length(lst) == 0


def test_init_dict():
    keys = FFI.init_vector(r.TYPE_SYMBOL, 2)
    values = FFI.init_list([FFI.init_i32(1), FFI.init_i32(2)])

    dct = FFI.init_dict(keys, values)
    assert isinstance(dct, r.RayObject)

    keys2 = FFI.init_vector(r.TYPE_SYMBOL, 1)
    with pytest.raises(RayforceLengthError):
        FFI.init_dict(keys2, values)


def test_init_table():
    columns = FFI.init_vector(r.TYPE_SYMBOL, 2)
    col1_vals = FFI.init_vector(r.TYPE_I64, 2)
    col2_vals = FFI.init_vector(r.TYPE_I64, 2)
    values = FFI.init_list([col1_vals, col2_vals])

    table = FFI.init_table(columns, values)
    assert isinstance(table, r.RayObject)

    columns2 = FFI.init_vector(r.TYPE_SYMBOL, 1)
    with pytest.raises(RayforceLengthError):
        FFI.init_table(columns2, values)


def test_push_obj():
    lst = FFI.init_list([FFI.init_i32(42)])
    FFI.push_obj(lst, FFI.init_i64(33))
    assert FFI.get_obj_length(lst) == 2


def test_insert_obj():
    vec = FFI.init_vector(r.TYPE_I64, 3)
    FFI.insert_obj(vec, 1, FFI.init_i64(42))
    assert FFI.get_obj_length(vec) == 4

    lst = FFI.init_list([FFI.init_i32(1), FFI.init_i32(2)])
    FFI.insert_obj(lst, 1, FFI.init_i64(99))
    assert FFI.get_obj_length(lst) == 3


def test_at_idx():
    vec = FFI.init_vector(r.TYPE_I64, 3)
    assert isinstance(FFI.at_idx(vec, 0), r.RayObject)


def test_get_obj_length():
    vec = FFI.init_vector(r.TYPE_I64, 5)
    assert FFI.get_obj_length(vec) == 5


def test_get_table_keys():
    columns = FFI.init_vector(r.TYPE_SYMBOL, 2)
    col1_vals = FFI.init_vector(r.TYPE_I64, 2)
    col2_vals = FFI.init_vector(r.TYPE_I64, 2)
    values = FFI.init_list([col1_vals, col2_vals])

    table = FFI.init_table(columns, values)
    assert isinstance(FFI.get_table_keys(table), r.RayObject)


def test_get_table_values():
    columns = FFI.init_vector(r.TYPE_SYMBOL, 2)
    col1_vals = FFI.init_vector(r.TYPE_I64, 2)
    col2_vals = FFI.init_vector(r.TYPE_I64, 2)
    values = FFI.init_list([col1_vals, col2_vals])

    table = FFI.init_table(columns, values)
    assert isinstance(FFI.get_table_values(table), r.RayObject)


def test_dict_get():
    keys = FFI.init_vector(r.TYPE_SYMBOL, 1)
    values = FFI.init_list([FFI.init_i32(42)])
    dct = FFI.init_dict(keys, values)

    assert isinstance(FFI.dict_get(dct, FFI.init_symbol("test")), r.RayObject)


def test_get_dict_keys():
    keys = FFI.init_vector(r.TYPE_SYMBOL, 1)
    values = FFI.init_list([FFI.init_i32(42)])
    dct = FFI.init_dict(keys, values)

    assert isinstance(FFI.get_dict_keys(dct), r.RayObject)


def test_get_dict_values():
    keys = FFI.init_vector(r.TYPE_SYMBOL, 1)
    values = FFI.init_list([FFI.init_i32(42)])
    dct = FFI.init_dict(keys, values)

    assert isinstance(FFI.get_dict_values(dct), r.RayObject)


def test_eval_str():
    expr = FFI.init_string("1")
    assert isinstance(FFI.eval_str(expr), r.RayObject)

    invalid_expr = FFI.init_string("invalid_expr_!!!")
    with pytest.raises((RuntimeError, RayforceError)):
        FFI.eval_str(invalid_expr)


def test_eval_obj():
    obj = FFI.init_i32(42)
    assert isinstance(FFI.eval_obj(obj), r.RayObject)


def test_quote():
    obj = FFI.init_i32(42)
    assert isinstance(FFI.quote(obj), r.RayObject)

    with pytest.raises(TypeError):
        FFI.quote(None)


def test_rc_obj():
    obj = FFI.init_i32(42)
    rc = FFI.rc_obj(obj)
    assert isinstance(rc, int)
    assert rc >= 0

    with pytest.raises(TypeError):
        FFI.rc_obj(None)


def test_binary_set():
    name = FFI.init_symbol("test_var")
    value = FFI.init_i32(42)
    FFI.binary_set(name, value)

    with pytest.raises((RuntimeError, RayforceError)):
        FFI.binary_set(FFI.init_i32(42), value)


def test_env_get_internal_fn_by_name():
    result = FFI.env_get_internal_fn_by_name("+")
    assert result is None or isinstance(result, r.RayObject)

    with pytest.raises(RuntimeError):
        FFI.env_get_internal_fn_by_name("ssssss")


def test_env_get_internal_name_by_fn_raises_notimplemented():
    """v2 has no reverse lookup — the stub raises NotImplementedError."""
    func = FFI.env_get_internal_fn_by_name("+")
    with pytest.raises(NotImplementedError):
        FFI.env_get_internal_name_by_fn(func)


def test_set_obj_attrs():
    obj = FFI.init_i32(42)
    FFI.set_obj_attrs(obj, 0)


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
        == "runtime: cannot be called from threads other than the initialization thread"
    )


# ---------------------------------------------------------------------------
# Object lifecycle / garbage collection behavior
# ---------------------------------------------------------------------------


def test_object_lifecycle_rc_after_create():
    """Verify that newly created objects have a valid reference count."""
    obj = FFI.init_i64(100)
    rc = FFI.rc_obj(obj)
    assert isinstance(rc, int)
    assert rc >= 0


def test_object_lifecycle_multiple_references():
    """Verify reference count behavior when the same ptr is stored in a list."""
    obj = FFI.init_i64(42)
    rc_before = FFI.rc_obj(obj)

    lst = FFI.init_list([obj, obj])
    rc_after = FFI.rc_obj(obj)

    # The ref count should not have decreased after creating a list holding the obj.
    assert rc_after >= rc_before
    assert FFI.get_obj_length(lst) == 2


def test_object_lifecycle_vector_elements():
    """Verify objects inside a vector remain accessible after creation."""
    vec = FFI.init_vector(r.TYPE_I64, [10, 20, 30])
    for i in range(3):
        elem = FFI.at_idx(vec, i)
        assert isinstance(elem, r.RayObject)
        val = FFI.read_i64(elem)
        assert val == [10, 20, 30][i]


def test_object_lifecycle_nested_containers():
    """Verify that nested containers (list-in-list) remain valid."""
    inner = FFI.init_list([FFI.init_i32(1), FFI.init_i32(2)])
    outer = FFI.init_list([inner])
    assert FFI.get_obj_length(outer) == 1

    retrieved_inner = FFI.at_idx(outer, 0)
    assert FFI.get_obj_length(retrieved_inner) == 2


def test_object_lifecycle_overwrite_variable():
    """Verify that overwriting a variable via binary_set does not corrupt state."""
    name = FFI.init_symbol("_test_lifecycle_var")
    FFI.binary_set(name, FFI.init_i64(1))
    FFI.binary_set(name, FFI.init_i64(2))

    # The second value should be the active one; no crash or corruption.
    result = FFI.eval_str(FFI.init_string("_test_lifecycle_var"))
    assert isinstance(result, r.RayObject)
    assert FFI.read_i64(result) == 2


# ---------------------------------------------------------------------------
# Large vector stress test
# ---------------------------------------------------------------------------


def test_large_vector_stress():
    """Create a large vector and verify length and boundary element access."""
    size = 100_000
    vec = FFI.init_vector(r.TYPE_I64, size)
    assert FFI.get_obj_length(vec) == size

    # Access first and last elements (should not segfault).
    first = FFI.at_idx(vec, 0)
    last = FFI.at_idx(vec, size - 1)
    assert isinstance(first, r.RayObject)
    assert isinstance(last, r.RayObject)


def test_large_vector_with_values():
    """Create a large vector from a Python list and verify values at boundaries."""
    size = 50_000
    items = list(range(size))
    vec = FFI.init_vector(r.TYPE_I64, items)
    assert FFI.get_obj_length(vec) == size

    assert FFI.read_i64(FFI.at_idx(vec, 0)) == 0
    assert FFI.read_i64(FFI.at_idx(vec, size - 1)) == size - 1


def test_large_list_stress():
    """Create a list with many elements via repeated push_obj."""
    lst = FFI.init_list([])
    count = 1_000
    for i in range(count):
        FFI.push_obj(lst, FFI.init_i64(i))
    assert FFI.get_obj_length(lst) == count

    # Spot-check first and last.
    assert FFI.read_i64(FFI.at_idx(lst, 0)) == 0
    assert FFI.read_i64(FFI.at_idx(lst, count - 1)) == count - 1
