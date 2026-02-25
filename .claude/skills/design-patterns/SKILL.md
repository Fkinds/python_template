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

## Rules

- Only introduce a pattern when a code smell justifies it (YAGNI)
- Protocol in `usecases/protocols/`; implementation in `infrastructure/adapters/`
- Concrete classes satisfying a Protocol: `*Impl` suffix
- Value objects are always `attrs.frozen(kw_only=True)`
- One use case class = one business operation
- DI wiring only in `infrastructure/containers/` (Composition Root)
