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

### Immutable Objects & Invariants

Encapsulate state and make invalid states **unconstructible**.

- Expose reads through `@property` only; never define setters.
- `attrs.frozen(kw_only=True)` blocks reassignment, so no
  setter exists by construction.
- Enforce invariants at build time (`@<field>.validator` /
  `__attrs_post_init__`), not in a separate `validate()` call.

```python
# Bad: mutable, validated after the fact (invalid state exists)
@attrs.define
class Money:
    amount: int

    def validate(self) -> None:
        if self.amount < 0:
            raise ValueError("amount must be >= 0")

# Good: frozen + invariant at construction (unconstructible if invalid)
@attrs.frozen(kw_only=True)
class Money:
    amount: int

    @amount.validator
    def _check(self, _attr: attrs.Attribute, value: int) -> None:
        if value < 0:
            msg = "amount must be >= 0"
            raise ValueError(msg)

    @property
    def is_zero(self) -> bool:
        return self.amount == 0
```

attrs validators raise `ValueError` / `TypeError`; the
interface layer converts them to `serializers.ValidationError`.

### Collections: set / frozenset First

Default to `set` / `frozenset` unless order, duplicates, or
index access carry meaning. Reach for `list` / `tuple` only
when one of those properties is required.

| Need | Type |
|---|---|
| Unique, unordered, immutable | `frozenset` |
| Unique, unordered, mutable | `set` |
| Order or index matters | `list` / `tuple` |
| Membership test (`x in ...`) | `set` / `frozenset` (O(1)) |

### Unbounded Iteration

For data whose size is unknown / large / externally sourced,
iterate lazily instead of materializing a `list`.

| Source | Bad | Good |
|---|---|---|
| QuerySet | `list(qs)` | `qs.iterator()` |
| Own generation | `[x for x in huge]` | `(x for x in huge)` |
| Aggregation | manual `for` + accumulator | `sum()` / `any()` / `all()` |

Materialize fully only when the size is bounded and known.

## Enum over StrEnum

Default to `enum.Enum`. A `StrEnum` member **is** a `str`, so
it silently leaks into string contexts and blurs the type
boundary.

| Use | Choice |
|---|---|
| Domain state / category | `enum.Enum` (convert via `.value`) |
| Integer-backed flags / codes | `enum.IntEnum` |
| Mandatory string interop (API / DB / JSON value) | `enum.StrEnum` |

```python
# Bad: StrEnum used as a plain domain category — leaks as str
class Status(enum.StrEnum):
    ACTIVE = "active"

# "active" == Status.ACTIVE is True → type distinction lost

# Good: Enum keeps the boundary; serialize explicitly
class Status(enum.Enum):
    ACTIVE = "active"

payload = {"status": Status.ACTIVE.value}  # explicit conversion
```

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
| Unbounded decorator | `@functools.cache` | `@lru_cache(maxsize=N)` | `cache` = `lru_cache(maxsize=None)` |
| View cache | Manual cache logic per view | `@cache_page(timeout)` | Declarative, consistent TTL |
| Object lookup | `Model.objects.get()` every time | `django.core.cache` + TTL | Reduce DB round-trips |
| Invalidation | Manual `cache.delete()` everywhere | `post_save` / `post_delete` signal | Centralized, automatic |
| Cache key | Hardcoded `"my_key"` | `f"{model}:{pk}:v{VER}"` | Namespaced, versionable |
| Stampede | Fixed TTL on hot keys | TTL + random jitter | Prevent thundering herd on expiry |
| Mutable values | Cache `list` / `dict` directly | Cache a copy or frozen type | Caller mutation corrupts cache |
| Sensitive data | Cache PII / tokens as-is | Exclude or encrypt before caching | Leak risk if cache is exposed |

```python
# Bad: lru_cache on method leaks self via cache reference
class Service:
    @lru_cache
    def compute(self, key: str) -> int: ...

# Good: cached_property for instance-bound memoization
class Service:
    @cached_property
    def expensive(self) -> int: ...

# Bad: functools.cache is unbounded (= lru_cache(maxsize=None))
@functools.cache
def fetch(key: str) -> str: ...

# Good: Django low-level cache with TTL
from django.core import cache as django_cache

def get_author(pk: int) -> Author:
    key = f"author:{pk}"
    author = django_cache.cache.get(key)
    if author is None:
        author = Author.objects.get(pk=pk)
        django_cache.cache.set(key, author, timeout=300)
    return author

# Good: TTL with jitter to prevent cache stampede
import random
BASE_TTL = 300
jitter = random.randint(0, 30)
django_cache.cache.set(key, value, timeout=BASE_TTL + jitter)
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
