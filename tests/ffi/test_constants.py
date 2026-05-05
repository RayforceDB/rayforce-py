"""
Regression guard for rayforce v2 type-code constants.

These values come from /Users/karim/rayforce2/include/rayforce.h and are
Python-visible via _rayforce_c.TYPE_*. If any assertion below fails, either
the C module or the v2 library drifted — investigate before bumping the
expected value.
"""

from rayforce import _rayforce_c as r


def test_v2_type_codes() -> None:
    assert r.TYPE_LIST == 0
    assert r.TYPE_B8 == 1
    assert r.TYPE_U8 == 2
    assert r.TYPE_I16 == 3
    assert r.TYPE_I32 == 4
    assert r.TYPE_I64 == 5
    assert r.TYPE_F32 == 6
    assert r.TYPE_F64 == 7
    assert r.TYPE_DATE == 8
    assert r.TYPE_TIME == 9
    assert r.TYPE_TIMESTAMP == 10
    assert r.TYPE_GUID == 11
    assert r.TYPE_SYMBOL == 12
    assert r.TYPE_STR == 13

    assert r.TYPE_TABLE == 98
    assert r.TYPE_DICT == 99

    assert r.TYPE_LAMBDA == 100
    assert r.TYPE_UNARY == 101
    assert r.TYPE_BINARY == 102
    assert r.TYPE_VARY == 103

    assert r.TYPE_NULL == 126
    assert r.TYPE_ERR == 127
