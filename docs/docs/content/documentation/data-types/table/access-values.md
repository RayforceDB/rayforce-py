# :material-table-eye: Access Table Values

Rayforce-Py provides a handy interface to access [:octicons-table-24: Table](overview.md) columns and values.

```python
>>> table: Table
>>> table.columns()
Vector([Symbol('symbol'), Symbol('time'), Symbol('bid'), Symbol('ask')])

>>> table.values()
List([
    Vector([Symbol('AAPL'), Symbol('AAPL'), Symbol('AAPL'), Symbol('GOOG'), Symbol('GOOG'), Symbol('GOOG')]),
    Vector([Time(datetime.time(9, 0, 0, 95000)), Time(datetime.time(9, 0, 0, 105000)), Time(datetime.time(9, 0, 0, 295000)), Time(datetime.time(9, 0, 0, 145000)), Time(datetime.time(9, 0, 0, 155000)), Time(datetime.time(9, 0, 0, 345000))]),
    Vector([F64(100.0), F64(101.0), F64(102.0), F64(200.0), F64(201.0), F64(202.0)]),
    Vector([F64(110.0), F64(111.0), F64(112.0), F64(210.0), F64(211.0), F64(212.0)])
])

>>> [column for column in [records[0] for records in table.values()]]
[Symbol('AAPL'), Time(datetime.time(9, 0, 0, 95000)), F64(100.0), F64(110.0)]
```
