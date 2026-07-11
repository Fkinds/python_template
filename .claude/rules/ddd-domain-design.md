# DDD: Domain Object Completeness

How to keep domain objects (entities, value objects, aggregates)
complete and always-valid. Complements the layer guide in
`ddd-architecture.md` and the immutability rules in
`python-conventions.md` §1.

## 1. Always-Valid Domain Model

- A domain object is **never** observable in an invalid state.
  Enforce every invariant **at construction**, not afterwards.
  - value objects / entities: `attrs.frozen(kw_only=True)` +
    `@<field>.validator` / `__attrs_post_init__`
  - "make invalid states unconstructible" — no construct-then-
    `validate()`
- Validators raise `ValueError` / `TypeError`; the interface
  layer converts them (see `exception-architecture.md`). Invalid
  entities surface as `EntityError` (422), not 500.

## 2. Entity vs Value Object

| | Identity | Equality | Mutability |
|---|---|---|---|
| **Value Object** | none | by value (all fields) | immutable |
| **Entity** | stable id | by id | state changes over its life |

- Default to a **Value Object**. Promote to an Entity only when
  the thing has a lifecycle and a continuous identity.
- **Inherit the `common` supertypes** — do not roll your own:
  - Entities subclass `common.domain.entities.supertype.Entity`
    (it supplies the `uuid7` `id` and **id-based equality**).
  - Value objects subclass
    `common.domain.entities.supertype.ValueObject`.
- Both are `attrs.frozen(kw_only=True)`. An Entity "changes" by
  producing a **new** frozen instance (`attrs.evolve(...)`), never
  by mutation.
- **Entity subclasses MUST decorate with
  `@attrs.frozen(kw_only=True, eq=False)`.** `eq=False` keeps the
  base's id-identity `__eq__`/`__hash__`; omitting it makes attrs
  regenerate equality over **all** fields and silently reverts to
  value-equality.

## 3. Aggregate & Aggregate Root

- An **Aggregate** is a consistency boundary: a cluster of
  objects that must be mutated together under one invariant set.
- The **Aggregate Root** is the only entry point. Outsiders hold
  a reference to the root only — never to internal members.
- Invariants that span members live **inside** the root and are
  checked when the root is (re)constructed.
- One transaction changes **one** aggregate. Reach other
  aggregates by **identity (id)**, never by embedding their
  object graph.

## 4. No Anemic Domain Model (ドメインモデル貧血症の禁止)

An **anemic domain model** — an entity/value object that is only
data (fields + getters/setters) while the rules that operate on it
sit in usecases, serializers, or models — is **forbidden**. Data
and the behavior that guards it must live together.

- Business logic belongs in `domain/` value objects / entities /
  domain services — **not** in Django models (persistence only)
  and not in serializers or usecases.
- Expose **intent-revealing behavior**, not raw state access:
  `order.cancel()`, not `order.status = "cancelled"`.
- Reads are exposed through `@property` only; there are no
  setters (frozen enforces this).
- Logic that naturally spans multiple aggregates goes in a
  **domain service** (`domain/services/`), still stdlib + attrs
  only — this is the *only* sanctioned place for logic outside an
  entity, never a usecase reaching into an entity's fields.

**Detection signals** (any one = anemic, fix the design):

| Smell | Fix |
|---|---|
| Entity has only fields + get/set, no methods | Move the rule that reads those fields onto the entity |
| A usecase mutates entity state field-by-field | Replace with one intent-revealing method on the root |
| A rule about an entity lives in a serializer / model | Pull it into `domain/` (entity or domain service) |
| Same validation repeated by every caller | Push it into the object's construction / a value object |

## 5. Completeness (Totality)

- A domain type models the **whole** valid range and **only** the
  valid range: unrepresentable states should be impossible to
  build (use `Enum`, `frozenset`, narrow value objects instead of
  bare `str` / `int`).
- Prefer a small value object (`Email`, `Isbn`, `Money`) over a
  primitive when the primitive has rules — push the rules into
  the type so every caller inherits them ("no primitive
  obsession").

## Rules

- Enforce all invariants at construction; never expose an invalid
  state (no construct-then-validate)
- Value object by default; Entity only for things with identity +
  lifecycle; both `attrs.frozen(kw_only=True)`
- Inherit the `common` supertypes: entities extend `Entity`, value
  objects extend `ValueObject`; entity subclasses add `eq=False`
  to keep the base's id-based equality (never all-field equality)
- Mutate an aggregate only through its root; reference other
  aggregates by id, one aggregate per transaction
- **No anemic domain model** (ドメインモデル貧血症の禁止): behavior
  lives on the domain object / service, never as data-only entities
  with the rules stranded in models, serializers, or usecases
- Model exact valid ranges with `Enum` / value objects — no
  primitive obsession, no anemic setters
