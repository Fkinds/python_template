---
name: design-patterns
description: Design patterns and refactoring reference for this DDD/Django project. Use when refactoring code, resolving code smells, or deciding which pattern to apply.
---

# Design Patterns Reference

Patterns used in this project and when to apply them during
refactoring.

## Pattern Catalog

| Pattern | When to Apply | Implementation |
|---|---|---|
| **Protocol (Port)** | Decouple layers; define abstract boundaries | `typing.Protocol` + `@runtime_checkable` in `usecases/protocols/` |
| **Adapter** | Connect external systems to domain ports | Concrete class with `*Impl` suffix in `infrastructure/adapters/` |
| **Strategy** | Swap behavior at runtime (e.g. notifiers) | Inject a Protocol into use case via DI |
| **Factory** | Encapsulate complex object creation | Factory class in `infrastructure/factories/` |
| **DI Container** | Wire object graph in one place | `injector.Module` in `infrastructure/containers/` (Composition Root) |
| **Value Object** | Immutable domain data with validation | `attrs.frozen(kw_only=True)` in `domain/` |
| **Use Case** | Isolate a single business operation | Class with `execute()` in `usecases/`, keyword-only args |
| **Template Method** | Customize framework hook points | Override `get_serializer_class()` / `perform_create()` in ViewSets |
| **Repository** | Abstract persistence access | Interface in `usecases/protocols/`, impl in `interfaces/repositories/` |

## Refactoring Triggers

| Code Smell | Suggested Pattern | Example |
|---|---|---|
| `if/elif` switching on type or mode | **Strategy** | Replace conditionals with injected Protocol impl |
| Direct external API calls in business logic | **Adapter** | Extract behind a Protocol; impl in infrastructure |
| Constructor builds its own dependencies | **DI Container** | Move wiring to Composition Root |
| Mutable data passed across layers | **Value Object** | Replace with `attrs.frozen` |
| Large function doing multiple concerns | **Use Case** | Extract each concern into its own use case class |
| Duplicated object construction logic | **Factory** | Centralize creation in a factory class |
| Business logic in views or models | **Use Case + Repository** | Move logic to use case; data access to repository |

## Abstraction & Typing Choices

### Protocol vs ABC

| Use | Choice | Why |
|---|---|---|
| Define a port a layer depends on | `typing.Protocol` | Structural — implementers need not import or inherit; type checked statically |
| Retro-fit a type you do not own | `Protocol` | Conformance is by shape, addable after the fact |
| Force subclasses to implement at runtime | `abc.ABC` | Instantiating an incomplete subclass raises immediately |

This project's ports are Protocols in `usecases/protocols/`;
reach for `ABC` only when runtime enforcement of a base class
is genuinely required.

### Variance (generic parameters)

| Position | Variance | Example |
|---|---|---|
| Output / return | covariant | a `Producer[Cat]` is a `Producer[Animal]` |
| Input / consume | contravariant | a `Consumer[Animal]` is a `Consumer[Cat]` |
| Mutable container | invariant | `list[Cat]` is **not** `list[Animal]` |

Type read-only producers covariant, sink-only consumers
contravariant, and anything mutable invariant.

### Mixin initialization

A mixin in a cooperative MRO must call
`super().__init__(**kwargs)` — skipping it silently drops the
rest of the chain's initialization. Pass `**kwargs` through so
every base in the MRO is initialized.

## Design Signals From Tests

| Test pain | Hidden design problem | Pattern |
|---|---|---|
| Want to test a private method directly | A second responsibility is buried inside | Extract it into its own class (Use Case / Value Object) |
| Many `mock.patch` to construct the SUT | Dependencies hard-wired, no seam | Inject a Protocol (Port) via DI |
| Domain test needs a DB | Logic leaked into the repository | Pull logic into a pure domain function |

## Rules

- Only introduce a pattern when a code smell justifies it (YAGNI)
- Protocol in `usecases/protocols/`; implementation in `infrastructure/adapters/`
- Concrete classes satisfying a Protocol: `*Impl` suffix
- Value objects are always `attrs.frozen(kw_only=True)`
- One use case class = one business operation
- DI wiring only in `infrastructure/containers/` (Composition Root)
