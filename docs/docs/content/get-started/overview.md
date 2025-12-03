# :material-human-greeting-variant: Introduction to Rayforce-Py

Rayforce-Py is a powerful library which allows you to effectively execute statements inside RayforceDB runtime using handy Pythonic syntax.

```python
      table.select(
          total=table.amount.sum(),
          active_total=table.amount.where(table.status == "active").sum(),
          count=table.amount.count(),
      )
      .by("category")
      .execute()
      ┌──────────┬───────┬──────────────┬───────┐
      │ category │ total │ active_total │ count │
      ├──────────┼───────┼──────────────┼───────┤
      │ A        │ 600   │ 100          │ 3     │
      │ B        │ 400   │ 400          │ 2     │
      ├──────────┴───────┴──────────────┴───────┤
      │ 2 rows (2 shown) 4 columns (4 shown)    │
      └─────────────────────────────────────────┘
```

!!! note ""
    The interaction with the RayforceDB is happening via C API bus, which allows us to seamlessly operate with your local rayforce runtime with <b>little-to-no</b> practical overhead.

    This library is operating under <b>0 dependency</b> - it's run on pure python, without any external libraries.
    Read more about the underlying implementation in [:material-clock-fast: Performance](./performance.md) section.

## :octicons-package-16: Installation

Platform support info:

| Platform/Version                     | 3.11             | 3.12             | 3.13             |
| ------------------------------------ | ---------------- | ---------------- | ---------------- |
| :simple-linux: Linux x86_64          | :material-check: | :material-check: | :material-check: |
| :simple-apple: MacOS arm64           | :material-check: | :material-check: | :material-check: |
| :material-microsoft-windows: Windows | :material-close: `coming soon` |



> ### :simple-python: with pip (recommended)
Distribution is available via [pypi](https://pypi.org/project/rayforce-py/):
```bash
python -m pip install rayforce-py

# OR use available aliases:
python -m pip install rayforce
python -m pip install rayforcedb
```

> ### :simple-framework: from source
You can manually clone latest github repo and build it yourself
```bash
~ $ git clone https://github.com/RayforceDB/rayforce-py.git
~ $ cd rayforce-py

~/rayforce-py $ make all
# 1. Pulls the latest Rayforce from GitHub
# 2. Builds the Rayforce and it's plugins
# 3. Moves binaries around so they become available to the library

~/rayforce-py $ python -c "import rayforce; print(rayforce.version)"
0.0.5
```

## Discover

If you would like to become a contributor, please see [:simple-github: Contibuting](./contributing.md) section

If you are a developer, please see [:material-file-document: Documentation](../documentation/overview.md)
