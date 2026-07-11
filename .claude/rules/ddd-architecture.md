# DDD x Clean Architecture Layer Structure

Layer structure guide for modules adopting DDD.

## Layer Structure

```
module_name/
├── domain/              # Innermost: no external dependencies
│   ├── entities/        # Domain entities
│   ├── services/        # Domain services
│   └── (root modules)   # Value objects (attrs.frozen)
│
├── usecases/            # Depends only on domain
│   ├── protocols/       # Ports (typing.Protocol)
│   ├── _dto/            # Data transfer objects
│   └── adapters/        # Use-case adapters
│
├── interfaces/          # External-facing layer
│   ├── serializers/
│   ├── deserializers/
│   ├── repositories/
│   ├── adapters/
│   ├── factories/
│   ├── routing/
│   └── management/commands/
│
└── infrastructure/      # Outermost: may reference all layers
    ├── containers/      # DI containers (Composition Root)
    ├── adapters/        # External service implementations
    └── factories/       # Infrastructure factories
```

## Dependency Direction

```
domain ← usecases ← interfaces ← infrastructure
```

| Layer | Allowed Imports |
|---|---|
| domain | stdlib + `attrs` only |
| usecases | domain only |
| interfaces | domain + usecases |
| infrastructure/adapters | Implicitly satisfies Protocols |
| infrastructure/containers | All layers (Composition Root) |

## Library Mapping

| Purpose | Library | Location |
|---|---|---|
| Value objects / domain events | `attrs.frozen` | domain/ |
| Serializers (response) | `rest_framework.serializers` | interfaces/serializers/ |
| Deserializers (request) | `rest_framework.serializers` | interfaces/deserializers/ |
| Ports | `typing.Protocol` | usecases/protocols/ |

- Serializers and deserializers are both DRF
  `serializers.Serializer` today (separated by direction), **not**
  `attrs`. `attrs` is reserved for `domain/` value objects.
- `pydantic` boundary DTOs (`usecases/_dto/`) are **not yet used**
  — introduce them under YAGNI only when a real boundary needs
  parse + validate + serialize of external data. Why `domain/`
  stays `attrs` and a DTO layer would be `pydantic`: `attrs` needs
  no base class (keeps domain layer-pure), is `__slots__`+frozen
  immutable, and does not coerce types (invariants stay explicit);
  `pydantic` is for the untrusted-input edge where coercion,
  schema, and (de)serialization are wanted.

## Rules

- YAGNI: only create layers and directories as needed
- Value objects: `attrs.frozen(kw_only=True)`
- Extend the `common` base supertypes rather than rolling your own:
  domain `Entity` / `ValueObject`, and `Adapter` / `Factory` /
  `Repository` for infra/interface concretes (see
  `ddd-domain-design.md` for the entity `eq=False` requirement)
- HTTP boundary stays DRF: serializers/deserializers are
  `rest_framework.serializers` in `interfaces/` — do NOT migrate
  them to `pydantic` (it would re-implement ViewSet `is_valid` /
  400 handling / `serializers.ValidationError` → RFC9457)
- `pydantic` is for `usecases/_dto/` DTOs ONLY, added under YAGNI
  when a usecase boundary needs a typed object — never as the HTTP
  serialization layer
- DTOs (when introduced): `pydantic.BaseModel` (validation + serialization)
- Ports: `typing.Protocol`
- Concrete classes implementing a Protocol: `*Impl` suffix
- Use-case functions: keyword-only arguments
