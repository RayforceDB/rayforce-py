# :simple-python: Development

This section has all the necessary information for the developers who want to contribute to the library

### :material-pen: Lint

Rayforce-Py is using mypy and ruff to perform linting and typing across the library. Accessible with
```bash
make lint
```
!!! note ""
    This command runs a mypy daemon which checks that there are no types violation across the codebase,
    a ruff linter, which automatically fixes issues,
    a ruff formatter, which automatically fixes issues.

### :material-test-tube: Test

Rayforce-Py has a number of tests which are accessible with the makefile command:
```bash
make test
```
!!! note ""
    This command runs a full pytest suite against the codebase:
    
