---
name: unit-testing-strategy
description: >-
  Unit testing strategy guide based on Khorikov's principles.
  Use when deciding what to test, reviewing test scope, or
  evaluating test suite quality from a QA perspective.
---

# Unit Testing Strategy Guide

Based on Vladimir Khorikov, "Unit Testing Principles,
Practices, and Patterns" (2020).

## Purpose of Good Unit Tests

Good unit tests make a software project **sustainable**.

| Concept | Explanation |
|---|---|
| Code as liability | Code increases entropy; every change risks introducing disorder |
| Tests as safety net | Tests detect **regression** caused by code changes |
| Test code is also liability | Test code has bugs, requires maintenance, and adds cost |

Minimize both production code and test code. Keep only the
tests that earn their maintenance cost.

## Four Activities Around Tests

| Activity | Why |
|---|---|
| Refactor tests with production code | Tests coupled to old structure become false negatives |
| Run tests on every change | Catch regressions early |
| Fix false positives promptly | A test that fails for the wrong reason erodes trust |
| Read tests to understand behavior | Tests serve as living documentation |

## Unit = Unit of Behavior

A "unit" is **one unit of behavior**, not one unit of code.

| Principle | Bad | Good |
|---|---|---|
| Test target | Private method, single function | Observable outcome of a behavior |
| Verification | Internal state, call counts | Return value, side effect, output |
| Coupling | Test breaks on refactor | Test breaks only when behavior changes |

### Test Case Curation

Evaluate each test case and keep only those that are
necessary. Delete redundant or low-value tests.

| Keep | Delete |
|---|---|
| Verifies a distinct business rule | Duplicates another test's assertion |
| Catches a real regression risk | Tests trivial code (getters, pass-through) |
| Documents important behavior | Tests implementation detail |

## Test Priority by Layer

Focus unit tests on **business logic**. Other layers are
verified by integration / E2E tests.

| Layer (this project) | Unit Test Priority | Why |
|---|---|---|
| `domain/entities/` | **Highest** | Core business rules, value objects |
| `domain/services/` | **Highest** | Domain logic orchestration |
| `usecases/` | **High** | Application-level business rules |
| `interfaces/serializers/` | Low | Thin translation layer |
| `interfaces/repositories/` | Skip | Needs real DB → integration test |
| `infrastructure/` | Skip | External deps → integration / E2E |
| Glue code (urls, containers) | Skip | Configuration → E2E |

## QA Review Checklist

When reviewing a test suite, verify these criteria:

- [ ] Business logic paths are covered (happy + error)
- [ ] No test fails for the wrong reason (false positive)
- [ ] Tests run within acceptable time budget
- [ ] Test phase responsibilities are clearly separated
- [ ] Test descriptions explain **why**, not just **what**

## Test Phase Responsibilities

Unit tests do not guarantee external quality alone.
Assign responsibilities across test phases.

| Phase | Scope | Verifies |
|---|---|---|
| Unit test | Single behavior in isolation | Business rules, value objects, domain services, use cases |
| Integration test | Component + real dependency | DB queries, repository implementations, external API calls |
| System test | Full application stack | Cross-module interaction, middleware, authentication flow |
| E2E test | User-facing scenario | Complete user workflows, UI behavior |

### What Unit Tests Do NOT Guarantee

- Correct DB queries (→ integration test)
- API contract compliance (→ contract / integration test)
- UI rendering (→ E2E test)
- Performance under load (→ load test)

## Fixtures and Constructors

Do not use fixtures to construct the system under test (SUT).
Each test should create its own SUT directly.

| Scenario | Fixture Use |
|---|---|
| Tests need different constructor args | **Forbidden** — construct in each test |
| Integration test where all scenarios share the same instance | **Allowed as exception** |

The canonical exception is a database connection. A shared
base class may establish the connection in its constructor.

## Act Phase

The Act phase should ideally be **one line**. If it takes
more than one line, consider whether the SUT's API could be
better designed. This is a guideline, not an absolute rule
— use judgment on a case-by-case basis.

## Test Naming

`method under test` + `precondition` + `expected result`

The name should communicate **what is being verified** to
a non-developer who understands the problem domain.

## Parameterization

| Scenario | Parameterize? |
|---|---|
| Happy path | Usually no |
| Error cases with clear meaning | Yes |
| Complex behavior | No — write individual tests |

Splitting happy and error paths into separate parameterized
tests is acceptable only when each parameter's meaning is
self-evident.

## Test Quality

Test code must not be tightly coupled to **implementation
details** of the SUT. Tests that depend on algorithms or
internal logic steps are fragile.

| Quality | What is verified |
|---|---|
| Good test | Is the final result correct? |
| Bad test | Is the procedure correct? |

**Always prefer black-box testing over white-box testing.**

## Test Doubles

| Kind | Direction | Purpose |
|---|---|---|
| Stub | Inward | Controls input to the SUT |
| Mock | Outward | Verifies output from the SUT |

- Verifying communication with stubs is an
  **anti-pattern** (couples to implementation details)
- Public API → verify observable behavior
- Private API → implementation detail (do not verify)

## Testing Approaches

| Approach | Verifies | Priority |
|---|---|---|
| Output-value testing | Return values | **Highest** — simplest and least fragile |
| State-based testing | Object state after operation | High |
| Communication-based testing | Outgoing calls | Low — fragile due to mock dependency |

Prefer output-value > state-based > communication-based.

## Rules

- Test one behavior per test method, not one function
- Prioritize `domain/` and `usecases/` for unit testing
- Delete tests that only verify implementation details
- Do not unit-test infrastructure; use integration tests
- Review test suites periodically for false positives
- Act phase should ideally be a single line
- Prefer black-box testing over white-box testing
- Do not verify interactions with stubs
- Prefer output-value testing over state-based testing
