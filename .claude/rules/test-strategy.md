# Test Strategy: Sizes & Models

Classify tests by **size** (what they may touch + how fast),
not by the fuzzy "unit / integration / E2E" labels. Source:
Google Test Sizes. Deep reference + layer tables live in the
`unit-testing-strategy` skill.

## 1. Test Sizes

| Size | May use | Forbidden | Time |
|---|---|---|---|
| **Small** | in-process memory / computation only | network, file I/O, DB, system clock, `sleep`, threads | < 100ms |
| **Medium** | `localhost` (DB container, test HTTP server), temp files, subprocess | external internet | < 1s |
| **Large** | anything (real external API, full stack, browser) | — | seconds–min |

- **Small ban list is strict**: no `requests.get`, no
  `open(...)`, no DB connection, no direct `datetime.now()`
  (inject it via DI), no `time.sleep`, no waiting on threads.
- Django's `TestCase` with a real DB is **Medium**, not Small
  — judge by behavior, not by the framework's naming.
- **Large is not per-commit**: run it pre-merge / nightly /
  pre-release. Keep it sparse — it is slow, flaky, non-parallel.

## 2. Default to Small

Decision flow:

```
Hits external internet?            → Large
Uses localhost DB / file I/O?      → Medium
Depends on clock / random / threads?
  → inject the dependency → Small (else Medium)
Otherwise                          → Small
```

When a test "can only be Medium/Large," first try to **extract
the logic into a pure function / inject the dependency** so the
Medium part shrinks to the thin "edge" layer.

## 3. Test Model

Pick a shape by project nature; whatever the model, **keep
Large few**.

| Project nature | Model |
|---|---|
| Logic-rich domain (finance, business rules) | Pyramid (Small-heavy) |
| Web frontend / SPA | Trophy (static + integration) |
| Microservice / thin API wrapper | Honeycomb (Medium-heavy) |
| Unsure / ordinary web app | Start Pyramid, adjust where it hurts |

## 4. Layer → Size (this project)

| Layer | Size |
|---|---|
| `domain/` logic, value objects | Small |
| `usecases/` (deps mocked via DI) | Small |
| `interfaces/repositories/` (real DB) | Medium |
| API handlers (test client + DB) | Medium |
| external API clients (thin wrapper) | Small (stub HTTP) + contract test |
| migrations | Medium |

Common smell: "domain logic needs a DB" → logic has leaked into
the repository; extract it as a pure function and test it Small.

## Rules

- Classify every test as Small / Medium / Large by its ban list
- Default to Small; inject clock / random / I/O to stay Small
- A real DB or `localhost` makes a test Medium, not Small
- Keep Large sparse; do not run it on every commit
- `domain/` and `usecases/` tests must be Small (no DB / I/O)
