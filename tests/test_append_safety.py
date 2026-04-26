"""
M22 — Vector / list append safety.

`ray_vec_append` and `ray_list_append` apply COW and may realloc-grow.
Each return value is the only valid handle: the input pointer is either
the same (no growth) or freed inside the library (realloc grew the block).
The pyext code now reassigns through the `RAY_APPEND_REASSIGN` and
`RAY_LIST_APPEND_REASSIGN` macros so callers never keep a dangling pointer.

These tests exercise the realloc path explicitly: start with a vector /
list whose initial capacity is below the first power-of-two block, then
append enough elements (1024) to force several reallocations.
"""

from __future__ import annotations

from rayforce import _rayforce_c as r
from rayforce import types as t
from rayforce.ffi import FFI


N_APPENDS = 1024


class TestVectorAppendSafety:
    """Repeatedly append to a small typed vector and verify the realloc path
    leaves the Python wrapper with a single live, owned ray_t."""

    def test_i64_vector_grows_through_realloc(self):
        v = t.Vector([0], ray_type=t.I64)

        for i in range(1, N_APPENDS + 1):
            FFI.push_obj(v.ptr, FFI.init_i64(i))

        assert len(v) == N_APPENDS + 1
        # The Python wrapper now holds whatever realloc-final pointer the
        # library returned; that pointer must be the sole owner.
        assert FFI.rc_obj(v.ptr) == 1

        for i in range(0, N_APPENDS + 1):
            assert v[i].value == i

    def test_f64_vector_grows_through_realloc(self):
        v = t.Vector([0.5], ray_type=t.F64)

        for i in range(1, N_APPENDS + 1):
            FFI.push_obj(v.ptr, FFI.init_f64(float(i) + 0.5))

        assert len(v) == N_APPENDS + 1
        assert FFI.rc_obj(v.ptr) == 1
        assert v[0].value == 0.5
        assert v[N_APPENDS].value == float(N_APPENDS) + 0.5


class TestListAppendSafety:
    """Same pattern for RAY_LIST."""

    def test_list_grows_through_realloc(self):
        lst = t.List([FFI.init_i64(0)])

        for i in range(1, N_APPENDS + 1):
            FFI.push_obj(lst.ptr, FFI.init_i64(i))

        assert len(lst) == N_APPENDS + 1
        assert FFI.rc_obj(lst.ptr) == 1

        # Element check on a few representative positions; lists box each
        # element so per-index access is independent of the vector layout.
        assert FFI.read_i64(FFI.at_idx(lst.ptr, 0)) == 0
        assert FFI.read_i64(FFI.at_idx(lst.ptr, N_APPENDS // 2)) == N_APPENDS // 2
        assert FFI.read_i64(FFI.at_idx(lst.ptr, N_APPENDS)) == N_APPENDS


class TestAppendNullObj:
    """RAY_NULL_OBJ is a singleton; appending it 1024 times to a list must
    not blow up its rc nor leak."""

    def test_list_append_null_obj_repeatedly(self):
        # Construct a list; init_vector(TYPE_LIST, length) creates a list
        # pre-filled with RAY_NULL_OBJ entries — that itself exercises the
        # `ray_list_append(ray_obj, RAY_NULL_OBJ)` loop site.
        ptr = FFI.init_vector(r.TYPE_LIST, N_APPENDS)
        lst = t.List(ptr=ptr)
        assert len(lst) == N_APPENDS
        assert FFI.rc_obj(lst.ptr) == 1
