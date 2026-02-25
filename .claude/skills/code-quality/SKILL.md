---
name: code-quality
description: Python code quality reference. Use when writing, reviewing, or optimizing Python code for best practices, performance, and exception handling.
---

# Python Code Quality Guide

## Function Parameters

- Avoid `*args` / `**kwargs`; use explicit parameter names
- Use `*` to enforce keyword-only arguments
- Order parameters by priority (most important first)
- For many parameters, pass a data object (`attrs`) instead

```python
# Bad
def do_something(**kwargs) -> None: ...

# Good
def do_something(*, foo: int, bar: str) -> None: ...
```

## Imports

- Import modules, not individual objects
- Never use wildcard (`*`) imports

```python
# Bad
from django.http import HttpResponse, HttpResponseRedirect

# Good
from django import http, shortcuts
```

## Immutability

Prefer immutable types when data does not need to change:

| Mutable | Immutable |
|---|---|
| `@attrs.define` | `@attrs.frozen` |
| `set` | `frozenset` |
| `list[T]` | `tuple[T, ...]` / `collections.abc.Sequence[T]` |

## attrs over dataclasses

Prefer `attrs` over `dataclasses`. `attrs` enables `__slots__`
by default, improving memory efficiency and performance.

## File Splitting

When a file grows too large, split it into a package with
private modules and a re-exporting `__init__.py`.

```
# Before
- something.py

# After
- something/
  - __init__.py   # re-export public API
  - _foo.py
  - _bar.py
```

## Performance Patterns

| Pattern | Bad | Good | Why |
|---|---|---|---|
| Membership test | `x in [1, 2, 3]` | `x in frozenset({1, 2, 3})` | O(1) hash lookup vs O(n) scan |
| String concat | `+=` in loop | `"".join(...)` | Single allocation vs repeated copy |
| List creation | `for` + `append()` | List comprehension | `LIST_APPEND` bytecode, no method lookup |
| Loop variable | `module.func()` in loop | Alias to local first | `LOAD_FAST` vs `LOAD_GLOBAL` |
| Aggregation | Manual `for` loop | `sum()`, `min()`, `max()` | C-level loop, no interpreter overhead |
| Merge iterables | `list_a + list_b` | `itertools.chain(a, b)` | Zero-copy iterator vs full copy |

## Exception Handling Anti-Patterns

| Anti-pattern | Problem | Fix |
|---|---|---|
| `except Exception` | Hides bugs and critical errors | Catch specific exceptions |
| Bare `except:` | Catches `SystemExit`, `KeyboardInterrupt` | Name the exception explicitly |
| `except: pass` | Silently swallows errors | Log the error |
| Exceptions for control flow | Slow and unclear intent | Use `if` / `.get()` instead |
| Not re-raising | Error never reaches caller | Add `raise` after logging |

```python
# Bad
try:
    value = data["key"]
except:
    pass

# Good
value = data.get("key")

# When catching is necessary: be specific + log
try:
    result = external_api.fetch()
except external_api.TimeoutError:
    logger.exception("API timeout")
    raise
```
