import uuid

from rayforce import types as t


def test_guid():
    u_id = uuid.uuid4()
    assert t.GUID(str(u_id)).value == u_id
    assert t.GUID(u_id).value == u_id
