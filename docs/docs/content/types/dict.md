# Dict (Dictionary)

The `Dict` type represents a key-value mapping in raypy. It's similar to Python dictionaries and provides efficient lookup and storage of associated data.

## Type Information

- **Type Code:** Dynamic (TYPE_DICT)
- **Key Types:** Any raypy type (typically symbols or strings)
- **Value Types:** Any raypy type (scalars, containers, nested structures)
- **Python Equivalent:** `dict`
- **Characteristics:** Key-value pairs, efficient lookup

## Usage

### Creating Dict Values

```python
from raypy.types.container import Dict

# From Python dictionary
user_data = Dict({
    "name": "Alice",
    "age": 29,
    "active": True,
    "score": 95.5
})

# From nested dictionary
config = Dict({
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp"
    },
    "cache": {
        "enabled": True,
        "ttl": 3600
    }
})
```

### Accessing Keys and Values

```python
user = Dict({"name": "Alice", "age": 29})

# Get keys and values
keys = user.keys()
values = user.values()

print(f"Keys: {[k.value for k in keys]}")
print(f"Values: {[v.value for v in values]}")
```

## Examples

### User Profile

```python
from raypy.types.container import Dict

# User profile data
profile = Dict({
    "user_id": 12345,
    "username": "alice_dev",
    "email": "alice@example.com",
    "first_name": "Alice",
    "last_name": "Johnson",
    "age": 29,
    "is_active": True,
    "subscription": "premium",
    "join_date": "2023-01-15"
})

print("User Profile:")
keys = profile.keys()
values = profile.values()

for key, value in zip(keys, values):
    key_str = key.value
    val_str = value.value if hasattr(value, 'value') else value
    print(f"  {key_str}: {val_str}")
```

### Application Configuration

```python
# System configuration
app_config = Dict({
    "app_name": "DataProcessor",
    "version": "1.2.3",
    "debug": True,
    "database": {
        "host": "localhost",
        "port": 5432,
        "username": "dbuser",
        "ssl_enabled": True
    },
    "logging": {
        "level": "INFO",
        "file": "/var/log/app.log",
        "max_size": 10485760,  # 10MB
        "backup_count": 5
    },
    "features": {
        "analytics": True,
        "caching": True,
        "compression": False
    }
})

print("Application Configuration:")
print(f"App: {app_config.keys()[0].value} -> {app_config.values()[0].value}")
print(f"Version: {app_config.keys()[1].value} -> {app_config.values()[1].value}")

# Access nested configuration
database_config = None
for key, value in zip(app_config.keys(), app_config.values()):
    if key.value == "database":
        database_config = value
        break

if database_config:
    print("Database Config:")
    for key, value in zip(database_config.keys(), database_config.values()):
        print(f"  {key.value}: {value.value}")
```

### API Response

```python
# REST API response
api_response = Dict({
    "status": "success",
    "code": 200,
    "message": "Data retrieved successfully",
    "data": {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"},
            {"id": 3, "name": "Charlie", "role": "user"}
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 5,
            "per_page": 10,
            "total_items": 47
        }
    },
    "timestamp": "2025-01-15T10:30:00Z"
})

print("API Response:")
for key, value in zip(api_response.keys(), api_response.values()):
    key_str = key.value
    if isinstance(value.value if hasattr(value, 'value') else value, dict):
        print(f"  {key_str}: [nested dict]")
    else:
        val_str = value.value if hasattr(value, 'value') else value
        print(f"  {key_str}: {val_str}")
```

### Product Catalog

```python
# E-commerce product
product = Dict({
    "id": "PROD-001",
    "name": "Wireless Headphones",
    "description": "High-quality wireless headphones with noise cancellation",
    "price": 199.99,
    "currency": "USD",
    "in_stock": True,
    "quantity": 50,
    "category": "Electronics",
    "tags": ["wireless", "audio", "bluetooth", "noise-cancellation"],
    "specifications": {
        "brand": "AudioTech",
        "model": "WT-500",
        "color": "Black",
        "weight": "250g",
        "battery_life": "30 hours"
    },
    "reviews": {
        "average_rating": 4.5,
        "total_reviews": 128,
        "five_star": 85,
        "four_star": 32,
        "three_star": 8,
        "two_star": 2,
        "one_star": 1
    }
})

print("Product Information:")
for key, value in zip(product.keys(), product.values()):
    key_str = key.value
    if hasattr(value, 'keys'):  # Nested dictionary
        print(f"  {key_str}:")
        for nested_key, nested_value in zip(value.keys(), value.values()):
            nested_key_str = nested_key.value
            nested_val_str = nested_value.value if hasattr(nested_value, 'value') else nested_value
            print(f"    {nested_key_str}: {nested_val_str}")
    else:
        val_str = value.value if hasattr(value, 'value') else value
        print(f"  {key_str}: {val_str}")
```

### Server Metrics

```python
# System monitoring data
server_metrics = Dict({
    "hostname": "web-server-01",
    "timestamp": "2025-01-15T10:30:00Z",
    "uptime": 86400,  # seconds
    "cpu": {
        "usage_percent": 65.2,
        "load_average": [1.5, 1.2, 0.8],
        "cores": 8
    },
    "memory": {
        "total_gb": 16,
        "used_gb": 10.5,
        "free_gb": 5.5,
        "usage_percent": 65.6
    },
    "disk": {
        "total_gb": 500,
        "used_gb": 320,
        "free_gb": 180,
        "usage_percent": 64.0
    },
    "network": {
        "bytes_sent": 1048576000,
        "bytes_received": 2097152000,
        "packets_sent": 1000000,
        "packets_received": 1500000
    }
})

print("Server Metrics:")
for key, value in zip(server_metrics.keys(), server_metrics.values()):
    key_str = key.value
    if hasattr(value, 'keys'):  # Nested metrics
        print(f"{key_str.upper()}:")
        for metric_key, metric_value in zip(value.keys(), value.values()):
            metric_key_str = metric_key.value
            metric_val = metric_value.value if hasattr(metric_value, 'value') else metric_value
            print(f"  {metric_key_str}: {metric_val}")
    else:
        val_str = value.value if hasattr(value, 'value') else value
        print(f"{key_str}: {val_str}")
```

### Game State

```python
# Game player state
game_state = Dict({
    "player_id": "player_123",
    "level": 15,
    "experience": 2450,
    "health": 100,
    "mana": 80,
    "position": {
        "x": 125.5,
        "y": 230.8,
        "z": 45.0
    },
    "inventory": {
        "items": [
            {"name": "sword", "quantity": 1, "durability": 95},
            {"name": "potion", "quantity": 5, "type": "health"},
            {"name": "key", "quantity": 2, "material": "gold"}
        ],
        "capacity": 50,
        "weight": 12.5
    },
    "stats": {
        "strength": 18,
        "agility": 14,
        "intelligence": 12,
        "luck": 8
    },
    "achievements": ["first_kill", "level_10", "treasure_hunter"]
})

print("Game State:")
print(f"Player: {[k.value for k in game_state.keys() if k.value == 'player_id'][0]}")

# Find and display specific sections
for key, value in zip(game_state.keys(), game_state.values()):
    key_str = key.value
    if key_str in ["level", "experience", "health", "mana"]:
        val_str = value.value if hasattr(value, 'value') else value
        print(f"{key_str}: {val_str}")
```

### Database Schema

```python
# Table schema definition
table_schema = Dict({
    "table_name": "users",
    "columns": {
        "id": {
            "type": "INTEGER",
            "primary_key": True,
            "auto_increment": True
        },
        "username": {
            "type": "VARCHAR",
            "length": 50,
            "unique": True,
            "nullable": False
        },
        "email": {
            "type": "VARCHAR",
            "length": 100,
            "unique": True,
            "nullable": False
        },
        "created_at": {
            "type": "TIMESTAMP",
            "default": "CURRENT_TIMESTAMP"
        },
        "is_active": {
            "type": "BOOLEAN",
            "default": True
        }
    },
    "indexes": [
        {"name": "idx_username", "columns": ["username"]},
        {"name": "idx_email", "columns": ["email"]}
    ]
})

print("Database Schema:")
print(f"Table: {[v.value for k, v in zip(table_schema.keys(), table_schema.values()) if k.value == 'table_name'][0]}")
```

### Dictionary Comparison

```python
# Compare dictionaries
dict1 = Dict({"name": "Alice", "age": 29})
dict2 = Dict({"name": "Alice", "age": 29})
dict3 = Dict({"name": "Bob", "age": 30})

print("Dictionary Comparison:")
print(f"dict1 keys: {[k.value for k in dict1.keys()]}")
print(f"dict1 values: {[v.value for v in dict1.values()]}")

print(f"dict1 == dict2: {dict1 == dict2}")  # True (same keys and values)
print(f"dict1 == dict3: {dict1 == dict3}")  # False (different values)
```

### Working with Complex Keys

```python
from raypy.types.scalar import Symbol

# Using symbols as keys
symbol_dict = Dict({
    Symbol("user_name"): "Alice",
    Symbol("user_age"): 29,
    Symbol("user_active"): True
})

print("Symbol-keyed Dictionary:")
for key, value in zip(symbol_dict.keys(), symbol_dict.values()):
    key_str = key.value
    val_str = value.value if hasattr(value, 'value') else value
    print(f"  {key_str}: {val_str}")
```

## Notes

- Dictionaries store key-value pairs with efficient lookup
- Keys and values can be any raypy type
- Use `.keys()` to get a vector of all keys
- Use `.values()` to get a list of all values
- Supports nested dictionaries and complex data structures
- Key order is preserved (insertion order)
- Comparison works between dictionaries with same keys and values
- Ideal for configuration, structured data, API responses, and mappings
- More efficient than lists for data lookup by key
- Keys should be hashable and unique within the dictionary 