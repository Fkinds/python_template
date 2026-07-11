# Python Conventions

Cross-cutting Python coding mandates. Complements the
`Code style` section of CLAUDE.md and the deep references in
the `code-quality` and `unit-testing-strategy` skills.

## 1. Immutable Objects & Invariants

- Model domain data as immutable objects.
- Encapsulate state: expose reads through `@property` only.
  Never define setters.
- Use `attrs.frozen(kw_only=True)` (assignment is blocked, so
  no setter is possible).
- Enforce invariants **at construction time** so an invalid
  state can never be instantiated.
  - attrs: `@<field>.validator` or `__attrs_post_init__`
  - non-attrs: validate inside `__init__` and raise
- "Make invalid states unconstructible" — do NOT construct
  first and validate later.
- attrs validators raise `ValueError` / `TypeError`; these are
  converted to `serializers.ValidationError` at the interface
  layer (see `exception-architecture.md`).

| Bad | Good |
|---|---|
| Public mutable attr + setter | `attrs.frozen` + read-only `@property` |
| `obj.validate()` after construction | Validator / `__attrs_post_init__` on build |
| Exposed mutable field | Private field + `@property` accessor |

## 2. Collections: set / frozenset First

- Default to `set` / `frozenset` unless order, duplicates, or
  index access carry meaning (`frozenset` if immutable, `set`
  if mutable). They are more memory- and lookup-friendly.
- Membership tests (`x in ...`) MUST use `set` / `frozenset`
  (O(1) hash lookup, not O(n) scan).
- Use `list` / `tuple` only when ordering matters, duplicates
  are allowed, or elements are accessed by index.
- Reaffirms CLAUDE.md: order-insensitive constants use
  `frozenset`, not `list`.

## 3. Unbounded Iteration → Iterator

- For data whose size is unknown, large, or externally
  sourced, use an iterator / generator instead of
  materializing a `list`.
  - QuerySet: `.iterator()`
  - Own generation: generator expression `(... for ...)`
- Materialize the whole collection (`list(qs)`,
  `[x for x in huge]`) only when the size is bounded and known.
- Aggregate with `sum()` / `any()` / `all()` to keep the loop
  at C level and short-circuit where possible.

## 4. Enum over StrEnum

- Default to `enum.Enum` (or a purpose-specific variant such
  as `IntEnum`).
- Restrict `enum.StrEnum` to places where string interop is
  mandatory (e.g. matching external API / DB / JSON values
  directly).
- Why: a `StrEnum` member **is** a `str`, so it silently leaks
  into string contexts and blurs the type boundary.
- To preserve the distinction, use `Enum` and convert
  explicitly via `.value`.
- Qualifying exception: a domain enum whose members are written
  **directly** to an external store / wire and reconstructed from
  those strings (e.g. `notifications` `EventType` /
  `NotificationStatus` / `NotificationChannel` → Elasticsearch
  `keyword` fields + API JSON, rebuilt via an attrs `converter`)
  is mandatory string interop — keep it a `StrEnum`. Converting to
  `Enum` would only add `.value` at every boundary for no gain.

## 5. Tests: Heavy Mocking is a Design Smell

- A growing number of `mock.patch` / `MagicMock` in pytest is
  evidence of missing DI or poor seams — not a testing
  problem.
- Fix the **design**, not the test: inject dependencies via a
  `typing.Protocol` (port) and replace mocks with hand-written
  Stub / Fake doubles or a DI-container override.
- Reserve `mock.patch` for I/O boundaries that cannot be
  swapped through DI (last resort).
- See the `test-code-quality` and `unit-testing-strategy`
  skills for the full doubles taxonomy.

## 6. Language Gotchas

- Never use a mutable default argument (`def f(x=[])`). The
  default is evaluated once and shared across every call. Use
  `x=None` and build the default inside the body.
- Compare to `None` with `is` / `is not`, never `==` (it is a
  singleton; compare identity).
- Test truthiness directly (`if flag:` / `if not items:`), not
  `== True` or `len(...) == 0`.
- See the `code-quality` skill for examples and f-string vs
  lazy-logging formatting.

## Rules

- Immutable objects: `frozen` + `@property`, no setters,
  invariants checked at construction
- Make invalid states unconstructible (no construct-then-
  validate)
- Prefer `set` / `frozenset` when order / duplicates / index
  do not matter
- Membership tests use `set` / `frozenset`
- Unknown-size data uses iterator / generator; never
  materialize blindly
- Default to `Enum`; use `StrEnum` only when string interop is
  mandatory
- Treat heavy `mock.patch` usage as a design smell → introduce
  DI + Stub / Fake
- No mutable default arguments; compare to `None` with `is`;
  test truthiness directly
