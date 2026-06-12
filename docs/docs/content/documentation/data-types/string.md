# :material-card-text: String

The `String` type represents a sequence of characters. v2 has no separate character type — indexing or iterating a `String` yields length-1 `String` values.

You can initialize a `String` from any Python value that supports `str()` conversion. Access the underlying value via the `.value` property.

## Usage

```python
>>> from rayforce import String
>>> name = String("Hello, World!")
>>> name
String('Hello, World!')  # type: rayforce.String
>>> name.value
'Hello, World!'  # type: str
```

## Characters

v2 has no standalone `Char` (`C8`) type — a single character is simply a length-1 `String`:

```python
>>> name[0]
String('H')  # type: rayforce.String
>>> len(String("R"))
1
```
