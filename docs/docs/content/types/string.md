# String

The `String` type represents a string of characters in raypy. It's implemented as a vector of `C8` (character) types and provides string-like functionality.

## Type Information

- **Type Code:** `12` (TYPE_C8 for character vector)
- **Implementation:** Vector of C8 characters
- **Python Equivalent:** `str`
- **Characteristics:** Variable length, character-based

## Usage

### Creating String Values

```python
from raypy.types.container import String

# From string literals
name = String("Hello, World!")
greeting = String("Welcome to raypy")

# From other string-like objects
message = String("Multiple\nLines\nOf\nText")
```

### Accessing Values

```python
text = String("Hello")
print(text.value)  # "Hello"
print(type(text.value))  # <class 'str'>
```

## Examples

### Basic Usage

```python
from raypy.types.container import String

# Create strings
first_name = String("Alice")
last_name = String("Johnson")
email = String("alice.johnson@example.com")

print(f"First Name: {first_name.value}")
print(f"Last Name: {last_name.value}")
print(f"Email: {email.value}")

# String length
full_name = String("Alice Johnson")
print(f"Full name length: {len(full_name)}")
```

### Text Processing

```python
# Document content
document = String("raypy is a powerful data processing library")
print(f"Document: {document.value}")
print(f"Length: {len(document)} characters")

# Multi-line text
code_snippet = String("""
def hello_world():
    print("Hello, World!")
    return True
""")

print(f"Code snippet:")
print(code_snippet.value)
```

### User Input and Forms

```python
# User profile data
username = String("alice_developer")
bio = String("Software engineer passionate about data science and machine learning")
location = String("San Francisco, CA")
website = String("https://alice-dev.example.com")

print("User Profile:")
print(f"Username: {username.value}")
print(f"Bio: {bio.value}")
print(f"Location: {location.value}")
print(f"Website: {website.value}")
```

### Configuration and Settings

```python
# Application settings
app_name = String("DataProcessor")
version = String("1.2.3")
config_path = String("/etc/dataprocessor/config.json")
log_file = String("/var/log/dataprocessor.log")

print("Application Configuration:")
print(f"Name: {app_name.value}")
print(f"Version: {version.value}")
print(f"Config: {config_path.value}")
print(f"Logs: {log_file.value}")
```

### File and Path Handling

```python
# File system paths
home_dir = String("/home/alice")
project_dir = String("/home/alice/projects/raypy")
data_file = String("sensor_data.csv")
output_file = String("processed_results.json")

print("File System:")
print(f"Home: {home_dir.value}")
print(f"Project: {project_dir.value}")
print(f"Input: {data_file.value}")
print(f"Output: {output_file.value}")

# URLs and endpoints
api_base = String("https://api.example.com/v1")
auth_endpoint = String("/auth/login")
data_endpoint = String("/data/upload")

print(f"API Base: {api_base.value}")
print(f"Auth: {auth_endpoint.value}")
print(f"Data: {data_endpoint.value}")
```

### Data Validation

```python
# Email validation example
emails = [
    String("valid@example.com"),
    String("user.name@domain.co.uk"),
    String("invalid-email"),
    String("another@valid.org"),
]

print("Email Validation:")
for email in emails:
    email_str = email.value
    # Simple validation (contains @ and .)
    is_valid = "@" in email_str and "." in email_str.split("@")[-1]
    status = "✓" if is_valid else "✗"
    print(f"{status} {email_str}")
```

### Text Formatting and Templates

```python
# Message templates
welcome_template = String("Welcome, {name}! Your account has been created.")
error_template = String("Error {code}: {message}")
success_template = String("Operation completed successfully in {time}ms")

print("Message Templates:")
print(f"Welcome: {welcome_template.value}")
print(f"Error: {error_template.value}")
print(f"Success: {success_template.value}")

# Actual messages (using Python string formatting)
welcome_msg = String(welcome_template.value.format(name="Alice"))
error_msg = String(error_template.value.format(code=404, message="Not Found"))

print(f"\nFormatted Messages:")
print(f"Welcome: {welcome_msg.value}")
print(f"Error: {error_msg.value}")
```

### Database Content

```python
# Product descriptions
products = [
    {
        "id": 1,
        "name": String("Wireless Headphones"),
        "description": String("High-quality wireless headphones with noise cancellation"),
        "category": String("Electronics"),
    },
    {
        "id": 2,
        "name": String("Programming Book"),
        "description": String("Comprehensive guide to modern software development"),
        "category": String("Books"),
    },
]

print("Product Catalog:")
for product in products:
    print(f"ID: {product['id']}")
    print(f"Name: {product['name'].value}")
    print(f"Description: {product['description'].value}")
    print(f"Category: {product['category'].value}")
    print()
```

### Log Messages

```python
from datetime import datetime

# System log entries
log_entries = [
    String("System startup completed successfully"),
    String("Database connection established"),
    String("User authentication service started"),
    String("Cache warming completed in 2.3 seconds"),
]

print("System Log:")
for i, entry in enumerate(log_entries, 1):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {i:03d}: {entry.value}")
```

### String Comparison

```python
# Text comparison
text1 = String("Hello World")
text2 = String("Hello World")
text3 = String("Hello, World!")

print(f"Text 1: '{text1.value}'")
print(f"Text 2: '{text2.value}'")
print(f"Text 3: '{text3.value}'")

# Compare underlying string values
print(f"text1 == text2: {text1.value == text2.value}")  # True
print(f"text1 == text3: {text1.value == text3.value}")  # False
```

### Working with Special Characters

```python
# Unicode and special characters
unicode_text = String("Hello 🌍 World! 你好")
special_chars = String("Symbols: @#$%^&*()")
escaped_text = String("Line 1\nLine 2\tTabbed")

print(f"Unicode: {unicode_text.value}")
print(f"Special: {special_chars.value}")
print(f"Escaped: {repr(escaped_text.value)}")
```

### JSON and Serialization

```python
# JSON strings for data exchange
json_data = String('{"name": "Alice", "age": 30, "city": "San Francisco"}')
xml_data = String('<user><name>Alice</name><age>30</age></user>')
csv_data = String("name,age,city\nAlice,30,San Francisco")

print("Data Formats:")
print(f"JSON: {json_data.value}")
print(f"XML: {xml_data.value}")
print(f"CSV: {csv_data.value}")
```

### Search and Text Analysis

```python
# Text content for analysis
article = String("""
raypy is a high-performance data processing library designed for 
modern applications. It provides efficient data structures and 
operations for handling large datasets with ease.
""")

print(f"Article: {article.value}")
print(f"Character count: {len(article)}")

# Simple text analysis
content = article.value.lower()
keywords = ["raypy", "data", "performance", "library"]

print("\nKeyword Analysis:")
for keyword in keywords:
    count = content.count(keyword)
    print(f"'{keyword}': {count} occurrences")
```

## Notes

- `String` is implemented as a vector of `C8` characters
- Supports Unicode and special characters
- Variable length with dynamic sizing
- The underlying value is a Python `str` object
- Use for text data, file paths, URLs, and any string content
- More efficient than individual `C8` objects for multi-character strings
- Supports all standard string operations through the `.value` property
- Length can be obtained using `len(string_obj)`
- For single characters, use the `C8` scalar type instead
- Ideal for user input, configuration, logging, and text processing 