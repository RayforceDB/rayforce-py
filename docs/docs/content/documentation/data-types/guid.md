# :material-identifier: GUID

The `GUID` type represents a globally unique identifier. It is equivalent to Python's `uuid.UUID` type and stores a 16-byte identifier.

You can initialize a `GUID` from a `uuid.UUID`, a `str`, or 16 raw `bytes`.

Access the underlying value via the `.value` property.

```python
>>> from uuid import uuid4
>>> from rayforce import GUID

>>> guid = GUID(uuid4())  # from a uuid.UUID value
>>> guid
GUID(UUID('724f8738-2482-4bb8-aa62-f0e682a58a91'))

>>> guid = GUID("724f8738-2482-4bb8-aa62-f0e682a58a91")  # from a string
>>> guid
GUID(UUID('724f8738-2482-4bb8-aa62-f0e682a58a91'))

>>> guid = GUID(uuid4().bytes)  # from 16 raw bytes
>>> guid
GUID(UUID('6c099338-840d-4f50-beb5-ab39267e87ab'))

>>> guid.value
UUID('6c099338-840d-4f50-beb5-ab39267e87ab')
```
