---
name: lint-fix
description: Run all linters and formatters to fix code issues. Use when the user asks to lint, format, or fix style issues.
disable-model-invocation: true
---

Run all linting and formatting tools in order. Always use `uv run`.

## 1. Ruff lint (auto-fix)

```bash
uv run ruff check src tests --fix
```

## 2. Ruff format

```bash
uv run ruff format src tests
```

## 3. MyPy type check (strict)

```bash
uv run mypy src
```

## 4. Fixit custom lint rules

```bash
uv run fixit lint src tests
```

## Verify (no auto-fix, for CI)

```bash
uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src && uv run fixit lint src tests
```
