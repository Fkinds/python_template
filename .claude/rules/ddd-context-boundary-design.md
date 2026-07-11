# DDD: Context Boundary Definition

How to define and defend Bounded Context boundaries in this
project. Complements `ddd-architecture.md` (intra-context layers)
by governing what happens **between** contexts.

## 1. Bounded Context = First-Party Package

- Each first-party package is one **Bounded Context** with its own
  model and ubiquitous language: `authors`, `books`,
  `notifications`. `common` is shared kernel; `config` is wiring.
- Inside a context a term has **one** meaning. The same word may
  mean different things in different contexts (a "Book" in
  `books` need not equal a "Book" reference in `notifications`) —
  that is expected, not a bug to unify.
- Boundaries are enforced by `uv run lint-imports` (import-linter
  contracts in `pyproject.toml`): per-context DDD **layers** +
  **domain purity** (domain may not import django / rest_framework
  / injector / pydantic / httpx).

## 2. No Shared Model Across Contexts

- A context **must not** import another context's `domain/`
  directly. Sharing an entity across contexts couples their
  lifecycles and leaks language.
- Cross-context communication goes through a translation seam, not
  a shared object graph:
  - hold the other context's **id**, not its entity
  - convert at the edge via a DTO (`usecases/_dto/`, `pydantic`)
  - integrate through an **Anti-Corruption Layer** (an adapter /
    port in the consuming context) so the foreign model never
    reaches your `domain/`.

## 3. Context Mapping Patterns

Name the relationship between two contexts explicitly; pick one:

| Pattern | Use when |
|---|---|
| **Shared Kernel** | a small model is co-owned — this is `common`; keep it minimal |
| **Customer / Supplier** | downstream's needs shape the upstream API |
| **Conformist** | downstream simply accepts upstream's model as-is |
| **Anti-Corruption Layer (ACL)** | downstream must **not** be shaped by upstream → translate at a port |
| **Open Host Service / Published Language** | one context serves many → a stable published contract (DTO / event) |

- Default between two of our contexts: **ACL via a `Protocol`
  port** (defined in `usecases/protocols/`, implemented in
  `infrastructure/adapters/`), so the dependency is invertible and
  testable Small.

## 4. Notifications Is Downstream

- `notifications` reacts to what other contexts do; other contexts
  must not depend on `notifications`' internals. Trigger it
  through a port / published event, keeping the arrow pointing
  **into** notifications, never out of it.

## Rules

- One Bounded Context per first-party package; a term has a single
  meaning **within** a context (divergence across contexts is fine)
- Never import another context's `domain/`; cross a boundary by id
  + DTO + ACL (`Protocol` port), never by a shared entity
- Name every cross-context relationship (Shared Kernel / ACL /
  Published Language …); default to ACL via a port
- Keep `common` (shared kernel) minimal; keep `notifications`
  strictly downstream
- `uv run lint-imports` must pass — it is the boundary's
  enforcement, not a suggestion
