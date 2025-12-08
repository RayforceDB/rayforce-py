# :material-human-greeting-variant: Introduction to Rayforce-Py

Rayforce-Py is a powerful library which allows you to effectively execute statements inside RayforceDB runtime using handy Pythonic syntax.

```python
      table.select(
          total=Column("amount").sum(),
          active_total=Column("amount").where(Column("status") == "active").sum(),
          count=Column("amount").count(),
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
    Read more about the underlying implementation in [:material-clock-fast: Performance](./technical-details.md) section.


<div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-primary); margin: 2rem 0;">
  <div style="text-align: center; margin-bottom: 1.5rem;">
    <div style="font-size: 3rem; font-weight: 800; color: var(--gold-500); margin-bottom: 0.5rem;">+0.88%</div>
    <div style="color: var(--text-secondary); font-size: 1.1rem;">Average Overhead</div>
    <div style="color: var(--text-tertiary); font-size: 0.9rem; margin-top: 0.5rem;">Nearly identical to native performance</div>
  </div>
</div>


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

~/rayforce-py $ make app
# 1. Pulls the latest Rayforce from GitHub
# 2. Builds the Rayforce and it's plugins
# 3. Moves binaries around so they become available to the library

~/rayforce-py $ python -c "import rayforce; print(rayforce.version)"
0.0.10
```

## Discover

If you would like to become a contributor, please see [:simple-github: Contibuting](../documentation/development/overview.md) section

If you are a developer, please see [:material-file-document: Documentation](../documentation/overview.md)
