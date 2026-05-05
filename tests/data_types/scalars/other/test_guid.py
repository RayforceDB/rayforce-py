"""Comprehensive tests for the GUID scalar."""

from __future__ import annotations

import uuid

import pytest

from rayforce import GUID, errors

# ── Construction ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "v",
    [
        "00000000-0000-0000-0000-000000000000",
        "11111111-2222-3333-4444-555555555555",
        "deadbeef-cafe-babe-1337-feedfacecafe",
        "ffffffff-ffff-ffff-ffff-ffffffffffff",
    ],
)
def test_guid_construct_from_string(v):
    assert str(GUID(v).value) == v


def test_guid_zero():
    assert (
        str(GUID("00000000-0000-0000-0000-000000000000").value)
        == "00000000-0000-0000-0000-000000000000"
    )


def test_guid_max_value():
    assert (
        str(GUID("ffffffff-ffff-ffff-ffff-ffffffffffff").value)
        == "ffffffff-ffff-ffff-ffff-ffffffffffff"
    )


@pytest.mark.parametrize(
    "v",
    [
        str(uuid.UUID(int=0)),
        str(uuid.UUID(int=2**128 - 1)),
        str(uuid.UUID(int=12345)),
        str(uuid.UUID(int=2**64)),
    ],
)
def test_guid_round_trip_uuid_module(v):
    assert str(GUID(v).value) == v


def test_guid_construct_from_uuid_object():
    u = uuid.uuid4()
    g = GUID(str(u))
    assert str(g.value) == str(u)


@pytest.mark.parametrize(
    "v",
    [
        "not-a-guid",
        "abc",
        "12345",
        "00000000-0000-0000-0000-00000000000",
        "zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz",
    ],
)
def test_guid_invalid_format_raises(v):
    with pytest.raises((TypeError, ValueError, RuntimeError, errors.RayforceError)):
        GUID(v)


# ── Equality ─────────────────────────────────────────────────────────────────


def test_guid_eq_self():
    v = "11111111-2222-3333-4444-555555555555"
    assert GUID(v) == GUID(v)


def test_guid_neq_different():
    a = GUID("11111111-1111-1111-1111-111111111111")
    b = GUID("22222222-2222-2222-2222-222222222222")
    assert a != b


# ── Repr / str ───────────────────────────────────────────────────────────────


def test_guid_repr_contains_value():
    v = "deadbeef-cafe-babe-1337-feedfacecafe"
    assert v in repr(GUID(v))


def test_guid_repr_starts_with_class_name():
    assert repr(GUID("00000000-0000-0000-0000-000000000000")).startswith("GUID")


# ── to_python ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "v",
    [
        "00000000-0000-0000-0000-000000000000",
        "11111111-2222-3333-4444-555555555555",
        "deadbeef-cafe-babe-1337-feedfacecafe",
    ],
)
def test_guid_to_python_returns_uuid(v):
    out = GUID(v).to_python()
    assert isinstance(out, uuid.UUID)
    assert str(out) == v


# ── Type code ────────────────────────────────────────────────────────────────


def test_guid_type_code():
    from rayforce import _rayforce_c as r

    assert GUID.type_code == -r.TYPE_GUID


# ── Format invariance ────────────────────────────────────────────────────────


def test_guid_lowercase_hex():
    g = GUID("deadbeef-cafe-babe-1337-feedfacecafe")
    s = str(g.value)
    assert s.lower() == s


def test_guid_canonical_format():
    g = GUID("11111111-2222-3333-4444-555555555555")
    parts = str(g.value).split("-")
    assert [len(p) for p in parts] == [8, 4, 4, 4, 12]


# ── Multiple uuid4 round-trips ──────────────────────────────────────────────


@pytest.mark.parametrize("seed", list(range(20)))
def test_guid_uuid4_round_trips(seed):
    u = str(uuid.uuid4())
    assert str(GUID(u).value) == u
