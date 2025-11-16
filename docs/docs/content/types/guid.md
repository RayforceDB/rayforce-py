# GUID (Globally Unique Identifier)

The `GUID` type represents a globally unique identifier in raypy. It's equivalent to Python's `uuid.UUID` type and stores a 16-char identifier.


## Type Information

| Type | Rayforce Object Type Code |
|------|---------------------------|
| `GUID` | `-11` |


## Usage

### Creating GUID Values

```python
from raypy import GUID
import uuid

# From UUID objects
uuid_obj = uuid.uuid4()
guid_from_uuid = GUID(uuid_obj)

# From string representation
guid_from_string = GUID("550e8400-e29b-41d4-a716-446655440000")

# From bytes (16 bytes)
guid_bytes = uuid.uuid4().bytes
guid_from_bytes = GUID(guid_bytes)

# From bytearray
guid_from_bytearray = GUID(bytearray(guid_bytes))
```

### Accessing Values

```python
guid = GUID("550e8400-e29b-41d4-a716-446655440000")
print(guid.value)  # UUID object
print(str(guid.value))  # String representation
```
