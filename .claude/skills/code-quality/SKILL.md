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

## Memory & Resource Management

| Pattern | Bad | Good | Why |
|---|---|---|---|
| Large data | `list(queryset)` | `queryset.iterator()` | Avoid materializing all rows |
| File I/O | `f = open(...)` | `with open(...) as f:` | Guarantees resource release |
| Unbounded cache | `@lru_cache` | `@lru_cache(maxsize=128)` | No limit = memory leak |
| Bulk generation | `[x for x in huge]` | Generator `(x for x in huge)` | Lazy eval, O(1) memory |
| Huge response | `Response(huge_list)` | `StreamingHttpResponse` | Chunked transfer saves memory |
| Bulk DB write | `create()` in loop | `bulk_create(objs, batch_size=1000)` | Fewer round-trips + bounded memory |
| QuerySet eval | `len(qs)` / `if qs:` | `qs.count()` / `qs.exists()` | Aggregates in DB, no fetch |

## Caching Strategy

| Pattern | Bad | Good | Why |
|---|---|---|---|
| Method cache | `@lru_cache` on method | `@cached_property` | `lru_cache` prevents instance GC |
| Module-level | `@lru_cache` (maxsize=None) | `@lru_cache(maxsize=N)` | Bound size to prevent leak |
| View cache | Manual cache logic per view | `@cache_page(timeout)` | Declarative, consistent TTL |
| Object lookup | `Model.objects.get()` every time | `django.core.cache` + TTL | Reduce DB round-trips |
| Invalidation | Manual `cache.delete()` everywhere | `post_save` / `post_delete` signal | Centralized, automatic |
| Cache key | Hardcoded `"my_key"` | `f"{model}:{pk}:v{VER}"` | Namespaced, versionable |

```python
# Bad: lru_cache on method leaks self via cache reference
class Service:
    @lru_cache
    def compute(self, key: str) -> int: ...

# Good: cached_property for instance-bound memoization
class Service:
    @cached_property
    def expensive(self) -> int: ...

# Good: Django low-level cache with TTL
from django.core import cache as django_cache

def get_author(pk: int) -> Author:
    key = f"author:{pk}"
    author = django_cache.cache.get(key)
    if author is None:
        author = Author.objects.get(pk=pk)
        django_cache.cache.set(key, author, timeout=300)
    return author
```

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
