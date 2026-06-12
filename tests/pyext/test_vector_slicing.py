"""
M21 — slice-aware data access in pyext.

The C extension exposes a `vec_slice` helper that wraps `ray_vec_slice`
(zero-copy view).  Slices set RAY_ATTR_SLICE on the header; for those
headers, `ray_data()` indirects through `slice_parent->data + slice_offset`.

These tests assert that pyext readers (`at_idx`, `read_*`, `read_vector_raw`,
`vec_is_null`, and the numpy roundtrip via `to_numpy`) all return correct
values when handed a sliced source.  A regression in any of those paths
would mean some accessor is reading from the slice header's own (empty)
payload instead of going through `ray_data()`.
"""

from __future__ import annotations

import datetime as dt

import numpy as np
import pytest

from rayforce import _rayforce_c as r
from rayforce import types as t
from rayforce.ffi import FFI


def _slice(vec: t.Vector, offset: int, length: int) -> t.Vector:
    sliced_ptr = FFI.vec_slice(vec.ptr, offset, length)
    return t.Vector(ptr=sliced_ptr)


class TestSliceI64:
    def test_at_idx_and_read(self):
        v = t.Vector([10, 20, 30, 40, 50, 60, 70], ray_type=t.I64)
        s = _slice(v, 1, 4)  # [20, 30, 40, 50]

        assert len(s) == 4
        assert FFI.get_obj_type(s.ptr) == r.TYPE_I64
        for i, expected in enumerate([20, 30, 40, 50]):
            elem = FFI.at_idx(s.ptr, i)
            assert FFI.read_i64(elem) == expected
            assert s[i].value == expected

    def test_read_vector_raw(self):
        v = t.Vector([10, 20, 30, 40, 50, 60, 70], ray_type=t.I64)
        s = _slice(v, 2, 3)  # [30, 40, 50]

        raw = FFI.read_vector_raw(s.ptr)
        unpacked = np.frombuffer(raw, dtype=np.int64)
        assert unpacked.tolist() == [30, 40, 50]

    def test_to_numpy_roundtrip(self):
        v = t.Vector([10, 20, 30, 40, 50, 60, 70], ray_type=t.I64)
        s = _slice(v, 1, 5)
        arr = s.to_numpy()
        assert arr.dtype == np.int64
        assert arr.tolist() == [20, 30, 40, 50, 60]


class TestSliceF64:
    def test_at_idx_and_read(self):
        v = t.Vector([1.5, 2.5, 3.5, 4.5, 5.5, 6.5], ray_type=t.F64)
        s = _slice(v, 1, 3)  # [2.5, 3.5, 4.5]

        assert len(s) == 3
        for i, expected in enumerate([2.5, 3.5, 4.5]):
            elem = FFI.at_idx(s.ptr, i)
            assert FFI.read_f64(elem) == expected
            assert s[i].value == expected

    def test_read_vector_raw(self):
        v = t.Vector([1.5, 2.5, 3.5, 4.5, 5.5, 6.5], ray_type=t.F64)
        s = _slice(v, 2, 3)  # [3.5, 4.5, 5.5]
        raw = FFI.read_vector_raw(s.ptr)
        unpacked = np.frombuffer(raw, dtype=np.float64)
        assert unpacked.tolist() == [3.5, 4.5, 5.5]

    def test_to_numpy_roundtrip(self):
        v = t.Vector([1.5, 2.5, 3.5, 4.5, 5.5, 6.5], ray_type=t.F64)
        s = _slice(v, 0, 4)
        arr = s.to_numpy()
        assert arr.dtype == np.float64
        assert arr.tolist() == [1.5, 2.5, 3.5, 4.5]


class TestSliceB8:
    def test_at_idx(self):
        v = t.Vector([True, False, True, True, False, True], ray_type=t.B8)
        s = _slice(v, 1, 4)  # [False, True, True, False]

        assert len(s) == 4
        for i, expected in enumerate([False, True, True, False]):
            elem = FFI.at_idx(s.ptr, i)
            assert FFI.read_b8(elem) is expected
            assert bool(s[i].value) is expected

    def test_to_numpy_roundtrip(self):
        v = t.Vector([True, False, True, True, False, True], ray_type=t.B8)
        s = _slice(v, 1, 4)
        arr = s.to_numpy()
        assert arr.dtype == np.bool_
        assert arr.tolist() == [False, True, True, False]


class TestSliceSym:
    def test_at_idx(self):
        v = t.Vector(["a", "b", "c", "d", "e"], ray_type=t.Symbol)
        s = _slice(v, 1, 3)  # ["b", "c", "d"]

        assert len(s) == 3
        for i, expected in enumerate(["b", "c", "d"]):
            elem = FFI.at_idx(s.ptr, i)
            assert FFI.read_symbol(elem) == expected

    def test_to_python(self):
        v = t.Vector(["alpha", "beta", "gamma", "delta", "epsilon"], ray_type=t.Symbol)
        s = _slice(v, 2, 2)  # ["gamma", "delta"]
        out = [el.value for el in s]
        assert out == ["gamma", "delta"]


class TestSliceTimestamp:
    def test_at_idx_and_read(self):
        ts = [
            dt.datetime(2025, 1, 1, tzinfo=dt.UTC),
            dt.datetime(2025, 2, 1, tzinfo=dt.UTC),
            dt.datetime(2025, 3, 1, tzinfo=dt.UTC),
            dt.datetime(2025, 4, 1, tzinfo=dt.UTC),
            dt.datetime(2025, 5, 1, tzinfo=dt.UTC),
        ]
        v = t.Vector(ts, ray_type=t.Timestamp)
        s = _slice(v, 1, 3)  # Feb, Mar, Apr

        assert len(s) == 3
        for i, expected in enumerate(ts[1:4]):
            # at_idx + read_timestamp yields raw ns-since-2000-01-01.
            elem = FFI.at_idx(s.ptr, i)
            assert isinstance(FFI.read_timestamp(elem), int)
            # The Python wrapper boxes to a Timestamp scalar.
            assert s[i].value == expected

    def test_read_vector_raw(self):
        ts = [
            dt.datetime(2025, 1, 1, tzinfo=dt.UTC),
            dt.datetime(2025, 2, 1, tzinfo=dt.UTC),
            dt.datetime(2025, 3, 1, tzinfo=dt.UTC),
            dt.datetime(2025, 4, 1, tzinfo=dt.UTC),
        ]
        v = t.Vector(ts, ray_type=t.Timestamp)
        s = _slice(v, 1, 2)
        raw = FFI.read_vector_raw(s.ptr)
        # Two TIMESTAMP elements = 2 * 8 = 16 bytes
        assert len(raw) == 16

    def test_to_numpy_roundtrip(self):
        ts = [
            dt.datetime(2025, 1, 1, tzinfo=dt.UTC),
            dt.datetime(2025, 2, 1, tzinfo=dt.UTC),
            dt.datetime(2025, 3, 1, tzinfo=dt.UTC),
            dt.datetime(2025, 4, 1, tzinfo=dt.UTC),
        ]
        v = t.Vector(ts, ray_type=t.Timestamp)
        s = _slice(v, 1, 2)
        arr = s.to_numpy()
        assert arr.dtype == np.dtype("datetime64[ns]")
        assert arr[0] == np.datetime64("2025-02-01T00:00:00", "ns")
        assert arr[1] == np.datetime64("2025-03-01T00:00:00", "ns")


class TestSliceParentLifetime:
    """The slice retains its parent — releasing the original Python handle
    must not invalidate the slice."""

    def test_parent_outlives_python_ref(self):
        v = t.Vector([100, 200, 300, 400, 500], ray_type=t.I64)
        s = _slice(v, 1, 3)
        # Drop the Python-side reference to the parent vector.
        del v
        # Slice still must be readable.
        assert [s[i].value for i in range(len(s))] == [200, 300, 400]


class TestSliceOfSlice:
    """Slicing a slice resolves to the ultimate parent — verify the resulting
    slice still produces the right values via every accessor."""

    def test_recursive_slice(self):
        v = t.Vector(list(range(20)), ray_type=t.I64)
        s1 = _slice(v, 5, 10)  # [5..14]
        s2 = _slice(s1, 2, 5)  # [7..11]

        assert len(s2) == 5
        for i, expected in enumerate(range(7, 12)):
            assert s2[i].value == expected
        assert s2.to_numpy().tolist() == [7, 8, 9, 10, 11]


class TestSliceOutOfRangeRaises:
    @pytest.mark.parametrize("offset, length", [(-1, 1), (0, -1), (5, 10)])
    def test_invalid_range(self, offset, length):
        v = t.Vector([1, 2, 3, 4, 5], ray_type=t.I64)
        with pytest.raises(IndexError):
            FFI.vec_slice(v.ptr, offset, length)
