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
| **Aggregate Root** | Guard a cluster of objects under one invariant set | Frozen root entity in `domain/entities/`; sole mutation entry point |
| **Domain Service** | Logic spanning several aggregates | Stateless function/class in `domain/services/` (stdlib + attrs) |
| **Anti-Corruption Layer** | Consume another context without its model leaking in | Translate at a Protocol port; foreign model never reaches `domain/` |

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
| Anemic entity: only getters/setters, logic elsewhere | **Aggregate Root + Domain Service** | Move behavior onto the entity; cross-aggregate logic to a domain service |
| Bare primitive carrying rules (`str` email, `int` money) | **Value Object** | Wrap in `attrs.frozen` with a validator (no primitive obsession) |
| One context imports another's `domain/` | **Anti-Corruption Layer** | Cross by id + DTO through a Protocol port; translate at the edge |

## DDD Modeling

Deep reference for `rules/ddd-domain-design.md` (completeness)
and `rules/ddd-context-boundary-design.md` (boundaries).

### Value Object vs Entity

Default to a Value Object; promote to Entity only when the thing
has a continuous identity and a lifecycle.

```python
# Value Object — no identity, equal by value, rules baked in.
# Subclass common.domain.entities.supertype.ValueObject.
@frozen(kw_only=True)
class Isbn(ValueObject):
    value: str

    @value.validator
    def _check(self, _: object, v: str) -> None:
        if len(v.replace("-", "")) != 13:
            raise ValueError("ISBN must be 13 digits")


# Entity — stable identity, equality by id only.
# Subclass common.domain.entities.supertype.Entity (it supplies the
# uuid7 id + id-based __eq__/__hash__). eq=False is REQUIRED so
# attrs does not regenerate all-field equality on the subclass.
@frozen(kw_only=True, eq=False)
class Book(Entity):          # inherits `id: uuid.UUID`
    isbn: Isbn
    title: str
```

An Entity "changes" by producing a new frozen instance
(`attrs.evolve(book, title=new_title)`), never by mutation. Two
Books with the same `id` are equal even if other fields differ.

### Aggregate: mutate through the root, enforce invariants on build

```python
@frozen(kw_only=True, eq=False)
class Order(Entity):  # aggregate root; id + id-equality from Entity
    lines: tuple[OrderLine, ...]        # internal members
    status: OrderStatus

    def __attrs_post_init__(self) -> None:
        # invariant spanning members, checked at construction
        if self.status is OrderStatus.CONFIRMED and not self.lines:
            raise ValueError("confirmed order needs at least one line")

    def confirm(self) -> "Order":       # intent-revealing behavior
        return evolve(self, status=OrderStatus.CONFIRMED)
```

- Outsiders hold `Order`, never an `OrderLine` directly.
- One transaction mutates one aggregate; reference another
  aggregate by **id** (`author_id: AuthorId`), not by embedding
  its object graph.
- Logic touching two aggregates → a `domain/services/` function,
  not a method on either root.

### Anemic vs rich model (ドメインモデル貧血症)

The entity is data-only and the rule leaks into the usecase — the
usecase reads the entity's fields to make the decision. Forbidden.

```python
# BAD (anemic): Order is a bag of fields; the usecase owns the rule.
@frozen(kw_only=True)
class Order:
    status: OrderStatus
    lines: tuple[OrderLine, ...]

class ConfirmOrder:
    def execute(self, *, order: Order) -> Order:
        if not order.lines:                     # rule about Order...
            raise ValueError("no lines")        # ...living outside Order
        return evolve(order, status=OrderStatus.CONFIRMED)
```

```python
# GOOD (rich): the rule lives with the data it guards.
@frozen(kw_only=True)
class Order:
    status: OrderStatus
    lines: tuple[OrderLine, ...]

    def confirm(self) -> "Order":
        if not self.lines:
            raise ValueError("no lines")
        return evolve(self, status=OrderStatus.CONFIRMED)

class ConfirmOrder:
    def execute(self, *, order: Order) -> Order:
        return order.confirm()                  # usecase orchestrates only
```

The usecase orchestrates (load → call behavior → persist); it must
not *contain* the domain rule. Logic spanning two aggregates is the
one exception, and it goes in a `domain/services/` function.

### Anti-Corruption Layer between contexts

A context must not import another context's `domain/`. Depend on a
port; translate the foreign shape at the adapter so it never
reaches your domain.

```python
# books/usecases/protocols/author_gateway.py  (the port)
@runtime_checkable
class AuthorGateway(Protocol):
    def name_of(self, author_id: AuthorId) -> AuthorName: ...


# books/infrastructure/adapters/author_gateway_impl.py  (the ACL)
class AuthorGatewayImpl:
    # calls the authors context, returns *books'* value objects —
    # authors.domain types stop here and never leak inward.
    def name_of(self, author_id: AuthorId) -> AuthorName: ...
```

`uv run lint-imports` enforces this: per-context DDD layers +
domain purity are import-linter contracts in `pyproject.toml`.

### Context map (who depends on whom)

The full catalog of mapping patterns (incl. Customer/Supplier,
Conformist) is canonical in `rules/ddd-context-boundary-design.md`
§3. This table only pins how they apply **here** (the `Here` column).

| Relationship | Meaning | Here |
|---|---|---|
| **Shared Kernel** | co-owned minimal model | `common` — keep it small |
| **Anti-Corruption Layer** | translate, stay unshaped | default between our contexts |
| **Published Language** | stable contract for many | DTO / event boundary |
| **downstream only** | arrow points in, never out | `notifications` |

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
- One use case class = one business operation
- DI wiring only in `infrastructure/containers/` (Composition Root)
- The domain / aggregate / context-boundary MUSTs are canonical in
  `rules/ddd-domain-design.md`, `rules/ddd-context-boundary-design.md`,
  and `rules/ddd-architecture.md` — this skill holds their worked
  examples, not a second copy of the mandates
