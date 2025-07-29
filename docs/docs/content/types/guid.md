# GUID (Globally Unique Identifier)

The `GUID` type represents a globally unique identifier in raypy. It's equivalent to Python's `uuid.UUID` type and stores a 128-bit identifier.

## Type Information

- **Type Code:** `11`
- **Storage Size:** 128 bits (16 bytes)
- **Python Equivalent:** `uuid.UUID`
- **Format:** Standard UUID format (8-4-4-4-12 hexadecimal digits)

## Usage

### Creating GUID Values

```python
from raypy.types.container import GUID
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

## Examples

### Basic Usage

```python
from raypy.types.container import GUID
import uuid

# Generate new GUIDs
user_id = GUID(uuid.uuid4())
session_id = GUID(uuid.uuid4())
transaction_id = GUID(uuid.uuid4())

print(f"User ID: {user_id.value}")
print(f"Session ID: {session_id.value}")
print(f"Transaction ID: {transaction_id.value}")
```

### Working with String GUIDs

```python
# Known GUID values
app_guid = GUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
namespace_guid = GUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8")

print(f"Application: {app_guid.value}")
print(f"Namespace: {namespace_guid.value}")

# Verify format
print(f"App GUID string: {str(app_guid.value)}")
print(f"App GUID hex: {app_guid.value.hex}")
```

### GUID Generation Patterns

```python
import uuid

# Different UUID versions
guid_v1 = GUID(uuid.uuid1())  # Time-based
guid_v4 = GUID(uuid.uuid4())  # Random

print(f"Time-based UUID: {guid_v1.value}")
print(f"Random UUID: {guid_v4.value}")
print(f"Version v1: {guid_v1.value.version}")
print(f"Version v4: {guid_v4.value.version}")
```

### Byte Operations

```python
import uuid

# Create GUID from bytes
original_uuid = uuid.uuid4()
byte_data = original_uuid.bytes

# Create GUID from byte data
guid_from_bytes = GUID(byte_data)
print(f"Original: {original_uuid}")
print(f"From bytes: {guid_from_bytes.value}")
print(f"Equal: {original_uuid == guid_from_bytes.value}")

# Extract bytes from GUID
extracted_bytes = guid_from_bytes.value.bytes
print(f"Bytes equal: {byte_data == extracted_bytes}")
```

### Error Handling

```python
# Invalid GUID formats
invalid_guids = [
    "invalid-guid-format",
    "550e8400-e29b-41d4-a716",  # Too short
    "550e8400-e29b-41d4-a716-446655440000-extra",  # Too long
    "",  # Empty string
]

for invalid_guid in invalid_guids:
    try:
        guid = GUID(invalid_guid)
        print(f"Valid: {invalid_guid}")
    except ValueError as e:
        print(f"Invalid: {invalid_guid} -> {e}")

# Invalid byte lengths
try:
    short_bytes = b"short"  # Not 16 bytes
    guid = GUID(short_bytes)
except ValueError as e:
    print(f"Byte length error: {e}")
```

### Database Primary Keys

```python
import uuid

# User record IDs
users = [
    {"id": GUID(uuid.uuid4()), "name": "Alice"},
    {"id": GUID(uuid.uuid4()), "name": "Bob"},
    {"id": GUID(uuid.uuid4()), "name": "Charlie"},
]

print("User Database:")
for user in users:
    print(f"ID: {user['id'].value}, Name: {user['name']}")

# Finding user by ID
target_id = users[1]["id"].value
for user in users:
    if user["id"].value == target_id:
        print(f"Found user: {user['name']}")
        break
```

### Distributed System IDs

```python
import uuid

# Service instance identifiers
services = {
    "web_server": GUID(uuid.uuid4()),
    "database": GUID(uuid.uuid4()),
    "cache": GUID(uuid.uuid4()),
    "queue": GUID(uuid.uuid4()),
}

print("Service Registry:")
for service_name, service_id in services.items():
    print(f"{service_name}: {service_id.value}")

# Message correlation IDs
request_id = GUID(uuid.uuid4())
correlation_id = GUID(uuid.uuid4())

print(f"\nRequest tracking:")
print(f"Request ID: {request_id.value}")
print(f"Correlation ID: {correlation_id.value}")
```

### File and Document IDs

```python
import uuid

# Document management system
documents = [
    {
        "id": GUID(uuid.uuid4()),
        "filename": "report.pdf",
        "size": 1024000
    },
    {
        "id": GUID(uuid.uuid4()),
        "filename": "presentation.pptx",
        "size": 2048000
    },
]

print("Document Library:")
for doc in documents:
    print(f"File: {doc['filename']}")
    print(f"ID: {doc['id'].value}")
    print(f"Size: {doc['size']} bytes")
    print()
```

### Comparison and Equality

```python
import uuid

# Create identical GUIDs
guid_str = "550e8400-e29b-41d4-a716-446655440000"
guid1 = GUID(guid_str)
guid2 = GUID(guid_str)

# Create different GUID
guid3 = GUID(uuid.uuid4())

print(f"GUID 1: {guid1.value}")
print(f"GUID 2: {guid2.value}")
print(f"GUID 3: {guid3.value}")

print(f"GUID 1 == GUID 2: {guid1.value == guid2.value}")
print(f"GUID 1 == GUID 3: {guid1.value == guid3.value}")
```

### Namespace-based GUIDs

```python
import uuid

# Create namespace-based UUIDs (deterministic)
namespace = uuid.NAMESPACE_DNS
name1 = "example.com"
name2 = "api.example.com"

# UUID v5 (SHA-1 hash)
guid_v5_1 = GUID(uuid.uuid5(namespace, name1))
guid_v5_2 = GUID(uuid.uuid5(namespace, name2))

# Same input always produces same GUID
guid_v5_1_repeat = GUID(uuid.uuid5(namespace, name1))

print(f"Domain GUID: {guid_v5_1.value}")
print(f"API GUID: {guid_v5_2.value}")
print(f"Repeat GUID: {guid_v5_1_repeat.value}")
print(f"Deterministic: {guid_v5_1.value == guid_v5_1_repeat.value}")
```

### Practical Applications

```python
import uuid

# API key generation
api_keys = [GUID(uuid.uuid4()) for _ in range(3)]
print("Generated API Keys:")
for i, key in enumerate(api_keys, 1):
    print(f"Key {i}: {key.value}")

# Session management
class Session:
    def __init__(self, user_id):
        self.session_id = GUID(uuid.uuid4())
        self.user_id = user_id
    
    def __str__(self):
        return f"Session {self.session_id.value} for user {self.user_id}"

# Create user sessions
sessions = [
    Session("alice"),
    Session("bob"),
    Session("charlie"),
]

print("\nActive Sessions:")
for session in sessions:
    print(session)
```

## Notes

- GUIDs are 128-bit values ensuring global uniqueness
- String format must be valid UUID format (8-4-4-4-12 hex digits)
- Byte input must be exactly 16 bytes
- Invalid formats will raise `ValueError`
- The underlying value is a Python `uuid.UUID` object
- Supports all UUID versions (1, 3, 4, 5)
- Ideal for distributed systems, database primary keys, and unique identifiers
- Use `uuid.uuid4()` for random GUIDs
- Use `uuid.uuid5()` for deterministic, namespace-based GUIDs 