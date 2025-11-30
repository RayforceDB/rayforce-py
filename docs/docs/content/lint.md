# Lint

Rayforce-Py is using mypy and ruff to perform linting and typing across the library. Accessible with
```bash
make lint
```

- This command runs:
    - a mypy daemon which checks that there are no types violation across the codebase
    - a ruff linter, which automatically fixes issues
    - a ruff formatter, which automatically fixes issues
