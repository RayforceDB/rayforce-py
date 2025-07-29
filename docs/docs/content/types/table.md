# Table

The `Table` type represents a structured data table in raypy, similar to a DataFrame in pandas or a database table. It consists of named columns and rows of data.

## Type Information

- **Type Code:** Dynamic (TYPE_TABLE)
- **Structure:** Named columns with typed data
- **Python Equivalent:** pandas DataFrame (conceptually)
- **Characteristics:** Columnar data storage, typed columns

## Usage

### Creating Table Values

```python
from raypy.types.container import Table

# Create table with columns and data
columns = ["id", "name", "age", "salary"]
values = [
    [1, 2, 3, 4, 5],                                    # id column
    ["Alice", "Bob", "Charlie", "Diana", "Eve"],        # name column  
    [25, 30, 35, 28, 32],                              # age column
    [50000, 60000, 70000, 55000, 65000]                # salary column
]

employee_table = Table(columns=columns, values=values)
```

### Accessing Table Data

```python
# Get column names
columns = employee_table.columns()
print(f"Columns: {[col.value for col in columns]}")

# Get all data
data = employee_table.values()
print(f"Data: {[row for row in data]}")
```

## Examples

### Employee Database

```python
from raypy.types.container import Table

# Employee data table
columns = ["employee_id", "first_name", "last_name", "department", "salary", "hire_date"]
values = [
    [101, 102, 103, 104, 105],                                           # employee_id
    ["Alice", "Bob", "Charlie", "Diana", "Eve"],                         # first_name
    ["Johnson", "Smith", "Brown", "Wilson", "Davis"],                    # last_name
    ["Engineering", "Marketing", "Engineering", "HR", "Finance"],        # department
    [75000, 55000, 80000, 50000, 60000],                               # salary
    ["2023-01-15", "2023-02-01", "2022-11-20", "2023-03-10", "2023-01-25"]  # hire_date
]

employees = Table(columns=columns, values=values)

print("Employee Database:")
cols = employees.columns()
data = employees.values()

# Print header
print("| " + " | ".join([f"{col.value:12}" for col in cols]) + " |")
print("|" + "|".join(["-" * 14 for _ in cols]) + "|")

# Print rows
for row_idx in range(len(data[0])):  # Assuming all columns have same length
    row_values = []
    for col_idx in range(len(data)):
        cell_value = data[col_idx][row_idx]
        if hasattr(cell_value, 'value'):
            row_values.append(f"{cell_value.value:12}")
        else:
            row_values.append(f"{cell_value:12}")
    print("| " + " | ".join(row_values) + " |")
```

### Sales Data

```python
# Monthly sales table
sales_columns = ["month", "product", "units_sold", "revenue", "profit_margin"]
sales_data = [
    ["Jan", "Feb", "Mar", "Jan", "Feb", "Mar"],                    # month
    ["Widget A", "Widget A", "Widget A", "Widget B", "Widget B", "Widget B"],  # product
    [100, 120, 95, 80, 90, 110],                                  # units_sold
    [5000.0, 6000.0, 4750.0, 4000.0, 4500.0, 5500.0],           # revenue
    [0.25, 0.28, 0.22, 0.30, 0.32, 0.35]                         # profit_margin
]

sales_table = Table(columns=sales_columns, values=sales_data)

print("Sales Performance:")
columns = sales_table.columns()
data = sales_table.values()

# Group by product
products = {}
for i in range(len(data[0])):
    product = data[1][i].value if hasattr(data[1][i], 'value') else data[1][i]
    if product not in products:
        products[product] = []
    
    row_data = {}
    for j, col in enumerate(columns):
        col_name = col.value
        cell_value = data[j][i]
        row_data[col_name] = cell_value.value if hasattr(cell_value, 'value') else cell_value
    products[product].append(row_data)

for product, records in products.items():
    print(f"\n{product}:")
    total_units = sum(r['units_sold'] for r in records)
    total_revenue = sum(r['revenue'] for r in records)
    avg_margin = sum(r['profit_margin'] for r in records) / len(records)
    
    print(f"  Total Units: {total_units}")
    print(f"  Total Revenue: ${total_revenue:,.2f}")
    print(f"  Avg Margin: {avg_margin:.1%}")
```

### Student Grades

```python
# Academic records
grade_columns = ["student_id", "student_name", "subject", "grade", "credits"]
grade_data = [
    [1001, 1001, 1001, 1002, 1002, 1002],                        # student_id
    ["Alice", "Alice", "Alice", "Bob", "Bob", "Bob"],            # student_name
    ["Math", "Physics", "Chemistry", "Math", "Physics", "Biology"],  # subject
    [92, 88, 95, 85, 90, 78],                                    # grade
    [3, 4, 3, 3, 4, 4]                                           # credits
]

grades_table = Table(columns=grade_columns, values=grade_data)

print("Student Grades:")
columns = grades_table.columns()
data = grades_table.values()

# Calculate GPA by student
students = {}
for i in range(len(data[0])):
    student_id = data[0][i].value if hasattr(data[0][i], 'value') else data[0][i]
    student_name = data[1][i].value if hasattr(data[1][i], 'value') else data[1][i]
    grade = data[3][i].value if hasattr(data[3][i], 'value') else data[3][i]
    credits = data[4][i].value if hasattr(data[4][i], 'value') else data[4][i]
    
    if student_id not in students:
        students[student_id] = {"name": student_name, "total_points": 0, "total_credits": 0}
    
    students[student_id]["total_points"] += grade * credits
    students[student_id]["total_credits"] += credits

print("Student GPAs:")
for student_id, info in students.items():
    gpa = info["total_points"] / info["total_credits"]
    print(f"  {info['name']} (ID: {student_id}): {gpa:.2f}")
```

### Inventory Management

```python
# Warehouse inventory
inventory_columns = ["sku", "product_name", "category", "quantity", "unit_price", "location"]
inventory_data = [
    ["SKU001", "SKU002", "SKU003", "SKU004", "SKU005"],                    # sku
    ["Laptop", "Mouse", "Keyboard", "Monitor", "Webcam"],                  # product_name
    ["Electronics", "Peripherals", "Peripherals", "Electronics", "Electronics"],  # category
    [25, 150, 75, 40, 60],                                                 # quantity
    [899.99, 29.99, 79.99, 299.99, 89.99],                               # unit_price
    ["A1-B2", "C3-D4", "C3-D5", "A2-B3", "C1-D1"]                       # location
]

inventory_table = Table(columns=inventory_columns, values=inventory_data)

print("Inventory Report:")
columns = inventory_table.columns()
data = inventory_table.values()

# Calculate total value by category
categories = {}
for i in range(len(data[0])):
    category = data[2][i].value if hasattr(data[2][i], 'value') else data[2][i]
    quantity = data[3][i].value if hasattr(data[3][i], 'value') else data[3][i]
    price = data[4][i].value if hasattr(data[4][i], 'value') else data[4][i]
    
    if category not in categories:
        categories[category] = {"total_items": 0, "total_value": 0.0}
    
    categories[category]["total_items"] += quantity
    categories[category]["total_value"] += quantity * price

print("Inventory by Category:")
for category, stats in categories.items():
    print(f"  {category}:")
    print(f"    Items: {stats['total_items']}")
    print(f"    Value: ${stats['total_value']:,.2f}")
```

### Time Series Data

```python
# Sensor readings over time
sensor_columns = ["timestamp", "sensor_id", "temperature", "humidity", "pressure"]
sensor_data = [
    ["2025-01-15T10:00:00", "2025-01-15T10:05:00", "2025-01-15T10:10:00", 
     "2025-01-15T10:15:00", "2025-01-15T10:20:00"],                        # timestamp
    ["TEMP_01", "TEMP_01", "TEMP_01", "TEMP_02", "TEMP_02"],              # sensor_id
    [22.5, 23.1, 22.8, 24.2, 23.9],                                       # temperature
    [45.2, 46.1, 45.8, 47.3, 46.9],                                       # humidity
    [1013.2, 1013.5, 1013.1, 1012.8, 1013.0]                            # pressure
]

sensor_table = Table(columns=sensor_columns, values=sensor_data)

print("Sensor Data:")
columns = sensor_table.columns()
data = sensor_table.values()

# Show latest readings by sensor
sensors = {}
for i in range(len(data[0])):
    sensor_id = data[1][i].value if hasattr(data[1][i], 'value') else data[1][i]
    timestamp = data[0][i].value if hasattr(data[0][i], 'value') else data[0][i]
    temp = data[2][i].value if hasattr(data[2][i], 'value') else data[2][i]
    humidity = data[3][i].value if hasattr(data[3][i], 'value') else data[3][i]
    pressure = data[4][i].value if hasattr(data[4][i], 'value') else data[4][i]
    
    if sensor_id not in sensors or timestamp > sensors[sensor_id]["timestamp"]:
        sensors[sensor_id] = {
            "timestamp": timestamp,
            "temperature": temp,
            "humidity": humidity,
            "pressure": pressure
        }

print("Latest Sensor Readings:")
for sensor_id, reading in sensors.items():
    print(f"  {sensor_id}:")
    print(f"    Time: {reading['timestamp']}")
    print(f"    Temperature: {reading['temperature']}°C")
    print(f"    Humidity: {reading['humidity']}%")
    print(f"    Pressure: {reading['pressure']} hPa")
```

### Table Analysis

```python
# Analyze table structure
def analyze_table(table):
    columns = table.columns()
    data = table.values()
    
    print("Table Analysis:")
    print(f"  Columns: {len(columns)}")
    print(f"  Rows: {len(data[0]) if data else 0}")
    
    print("  Column Details:")
    for i, col in enumerate(columns):
        col_name = col.value
        col_data = data[i] if i < len(data) else []
        col_type = type(col_data[0]).__name__ if col_data else "Empty"
        print(f"    {col_name}: {len(col_data)} values, type: {col_type}")

# Analyze the employee table
analyze_table(employees)
```

### Table Comparison

```python
# Compare tables
table1 = Table(
    columns=["id", "name"],
    values=[[1, 2], ["Alice", "Bob"]]
)

table2 = Table(
    columns=["id", "name"], 
    values=[[1, 2], ["Alice", "Bob"]]
)

table3 = Table(
    columns=["id", "name"],
    values=[[1, 2], ["Alice", "Charlie"]]
)

print("Table Comparison:")
print(f"table1 == table2: {table1 == table2}")  # True (same structure and data)
print(f"table1 == table3: {table1 == table3}")  # False (different data)
```

## Notes

- Tables represent structured, columnar data with named columns
- Each column can contain values of any raypy type
- All columns should have the same number of rows for consistency
- Use `.columns()` to get a vector of column names
- Use `.values()` to get a list containing each column's data
- Ideal for structured data analysis, reporting, and data processing
- Similar to database tables or spreadsheet data
- Supports comparison between tables with same structure and data
- More structured than lists but more flexible than vectors
- Perfect for data science, analytics, and business intelligence applications 