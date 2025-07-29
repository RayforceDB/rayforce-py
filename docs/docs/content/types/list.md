# List

The `List` type represents a heterogeneous collection in raypy. Unlike vectors, lists can contain elements of different types, making them similar to Python lists.

## Type Information

- **Type Code:** Dynamic (TYPE_LIST)
- **Element Types:** Any raypy type (scalars, containers, nested lists)
- **Python Equivalent:** `list`
- **Characteristics:** Heterogeneous elements, dynamic length

## Usage

### Creating List Values

```python
from raypy.types.container import List

# From Python list
mixed_list = List([1, "hello", 3.14, True])

# From raypy objects
from raypy.types.scalar import I64, Symbol, F64, B8
typed_list = List([
    I64(42),
    Symbol("test"),
    F64(3.14),
    B8(True)
])

# Empty list
empty_list = List([])
```

### Accessing and Modifying Elements

```python
# Create and modify list
data = List([1, 2, 3])
print(f"Original: {[item.value for item in data]}")

# Modify elements
data[1] = "changed"
print(f"Modified: {[item.value for item in data]}")

# Access elements
print(f"First element: {data[0].value}")
print(f"Last element: {data[-1].value}")
```

## Examples

### Mixed Data Types

```python
from raypy.types.container import List
from raypy.types.scalar import I64, Symbol, F64, B8

# User profile with mixed data
user_profile = List([
    Symbol("user_id"),      # Field name
    I64(12345),            # User ID
    Symbol("alice_dev"),    # Username
    F64(29.5),             # Age
    B8(True),              # Is active
    Symbol("premium")       # Account type
])

print("User Profile:")
for i, item in enumerate(user_profile):
    print(f"  {i}: {item.value} ({type(item).__name__})")
```

### Configuration Data

```python
# Application configuration
config = List([
    "app_name",           # String
    "DataProcessor",      # String
    "version",           # String  
    [1, 2, 3],           # Nested list
    "debug",             # String
    True,                # Boolean
    "max_connections",   # String
    100                  # Integer
])

print("Configuration:")
for i in range(0, len(config), 2):
    key = config[i]
    value = config[i + 1] if i + 1 < len(config) else None
    if value is not None:
        key_val = key.value if hasattr(key, 'value') else key
        val_val = value.value if hasattr(value, 'value') else value
        print(f"  {key_val}: {val_val}")
```

### Nested Structures

```python
# Nested lists and complex data
nested_data = List([
    "users",
    List([
        List(["alice", 25, True]),
        List(["bob", 30, False]),
        List(["charlie", 28, True])
    ]),
    "settings",
    List([
        "theme", "dark",
        "language", "en",
        "notifications", True
    ])
])

print("Nested Data Structure:")
print(f"Length: {len(nested_data)}")

# Access nested elements
users_list = nested_data[1]
first_user = users_list[0]
print(f"First user: {[item.value for item in first_user]}")
```

### API Response Data

```python
# Simulated API response
api_response = List([
    "status",     "success",
    "code",       200,
    "data",       List([
        List(["id", 1, "name", "Product A", "price", 29.99]),
        List(["id", 2, "name", "Product B", "price", 39.99]),
        List(["id", 3, "name", "Product C", "price", 19.99])
    ]),
    "meta",       List([
        "total", 3,
        "page", 1,
        "per_page", 10
    ])
])

print("API Response:")
print(f"Status: {api_response[1].value}")
print(f"Code: {api_response[3].value}")

# Extract product data
products = api_response[5]  # data field
print(f"Products ({len(products)}):")
for product in products:
    product_data = {}
    for i in range(0, len(product), 2):
        key = product[i].value
        value = product[i + 1].value
        product_data[key] = value
    print(f"  {product_data}")
```

### Database Records

```python
# Database query results
records = List([
    List([1, "Alice", "alice@example.com", 29]),
    List([2, "Bob", "bob@example.com", 34]),
    List([3, "Charlie", "charlie@example.com", 28])
])

columns = List(["id", "name", "email", "age"])

print("Database Results:")
print("Columns:", [col.value for col in columns])
print("Records:")
for record in records:
    print("  ", [field.value for field in record])
```

### Event Log

```python
from datetime import datetime

# System events with mixed data
events = List([
    List(["login", "2025-01-15T10:30:00", "alice", True]),
    List(["file_upload", "2025-01-15T10:35:00", "document.pdf", 1024000]),
    List(["logout", "2025-01-15T11:00:00", "alice", 1800]),  # session duration
    List(["error", "2025-01-15T11:05:00", "database_timeout", 5.2])  # error duration
])

print("Event Log:")
for event in events:
    event_type = event[0].value
    timestamp = event[1].value
    data1 = event[2].value
    data2 = event[3].value
    
    print(f"[{timestamp}] {event_type}: {data1} -> {data2}")
```

### Form Data

```python
# Web form submission
form_data = List([
    "first_name", "Alice",
    "last_name", "Johnson", 
    "email", "alice@example.com",
    "age", 29,
    "subscribe", True,
    "interests", List(["programming", "data_science", "ai"]),
    "comments", "Looking forward to using raypy!"
])

print("Form Submission:")
for i in range(0, len(form_data), 2):
    field = form_data[i].value
    value = form_data[i + 1]
    
    if hasattr(value, '__iter__') and not isinstance(value.value if hasattr(value, 'value') else value, str):
        # Handle nested lists
        val_str = [item.value for item in value]
    else:
        val_str = value.value if hasattr(value, 'value') else value
    
    print(f"  {field}: {val_str}")
```

### Data Processing Pipeline

```python
# Pipeline stages with results
pipeline_results = List([
    "input",
    List([100, 200, 300, 400, 500]),
    
    "filter",
    List([200, 400]),  # Values > 150
    
    "transform", 
    List([2.0, 4.0]),  # Divided by 100
    
    "aggregate",
    6.0  # Sum of transformed values
])

print("Data Pipeline Results:")
for i in range(0, len(pipeline_results), 2):
    stage = pipeline_results[i].value
    result = pipeline_results[i + 1]
    
    if hasattr(result, '__iter__') and hasattr(result, '__len__'):
        result_str = [item.value for item in result]
    else:
        result_str = result.value if hasattr(result, 'value') else result
    
    print(f"{stage}: {result_str}")
```

### List Operations

```python
# List manipulation
data = List([1, 2, 3, 4, 5])

print(f"Original list: {[item.value for item in data]}")
print(f"Length: {len(data)}")

# Access elements
print(f"First: {data[0].value}")
print(f"Last: {data[-1].value}")
print(f"Middle: {data[2].value}")

# Iterate through list
print("All elements:")
for i, item in enumerate(data):
    print(f"  Index {i}: {item.value}")
```

### List Comparison

```python
# Compare lists
list1 = List([1, 2, 3])
list2 = List([1, 2, 3])
list3 = List([1, 2, 4])

print(f"List 1: {[item.value for item in list1]}")
print(f"List 2: {[item.value for item in list2]}")
print(f"List 3: {[item.value for item in list3]}")

print(f"list1 == list2: {list1 == list2}")  # True
print(f"list1 == list3: {list1 == list3}")  # False
```

### Complex Data Structures

```python
# Complex nested structure
complex_data = List([
    "users",
    List([
        List([
            "id", 1,
            "profile", List([
                "name", "Alice",
                "preferences", List([
                    "theme", "dark",
                    "language", "en",
                    "notifications", List([
                        "email", True,
                        "push", False,
                        "sms", True
                    ])
                ])
            ])
        ])
    ])
])

print("Complex Data Structure:")
print(f"Root level items: {len(complex_data)}")

# Navigate nested structure
users = complex_data[1]
first_user = users[0]
profile_index = None

# Find profile section
for i in range(0, len(first_user), 2):
    if first_user[i].value == "profile":
        profile_index = i + 1
        break

if profile_index:
    profile = first_user[profile_index]
    print("User profile found with", len(profile), "items")
```

## Notes

- Lists can contain elements of different types (heterogeneous)
- Supports nesting of lists, vectors, and other containers
- Length can be obtained using `len(list_obj)`
- Supports positive and negative indexing
- Index out of bounds raises `IndexError`
- Lists are iterable and support element access by index
- Comparison works between lists with same structure and values
- More flexible than vectors but may use more memory
- Ideal for mixed data, configuration, API responses, and complex data structures
- Use vectors when all elements are of the same type for better performance 