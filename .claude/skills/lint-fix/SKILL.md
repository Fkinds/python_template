---
name: lint-fix
description: Run all linters and formatters to fix code issues. Use when the user asks to lint, format, or fix style issues.
disable-model-invocation: true
---

Run all linting and formatting tools in order. Always use `uv run`.

All targets are `src tests lint_rules` — the same set CLAUDE.md and
`.pre-commit-config.yaml` use. Do not drop `lint_rules`.

## 1. Ruff lint (auto-fix)

```bash
uv run ruff check src tests lint_rules --fix
```

## 2. Ruff format

```bash
uv run ruff format src tests lint_rules
```

## 3. MyPy type check (strict)

```bash
uv run mypy src lint_rules
```

## 4. Fixit custom lint rules

```bash
uv run fixit lint src tests lint_rules
```

## 5. Import-linter (layer contracts)

```bash
uv run lint-imports
```

## Verify (no auto-fix, full chain — matches CLAUDE.md)

```bash
uv run ruff check src tests lint_rules && uv run ruff format --check src tests lint_rules && uv run mypy src lint_rules && uv run fixit lint src tests lint_rules && uv run lint-imports
```
