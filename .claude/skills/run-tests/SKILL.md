---
name: run-tests
description: Run the project test suite. Use when the user asks to run tests, verify changes, or check for regressions.
disable-model-invocation: true
---

Run tests with the following commands. Always use `uv run`.

## Unit tests (no DB required, parallel)

```bash
uv run pytest tests/unit --numprocesses auto
```

## Functional tests (requires PostgreSQL, parallel)

```bash
uv run pytest tests/functional --numprocesses auto
```

## Integration tests (sequential)

```bash
uv run pytest tests/integration
```

## Lint rule tests

```bash
uv run pytest tests/linting
```

## All tests

```bash
uv run pytest
```

## Single file or test case

```bash
uv run pytest tests/unit/test_example.py
uv run pytest tests/unit/test_example.py::TestClass::test_method
```
