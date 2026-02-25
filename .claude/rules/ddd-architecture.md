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
| Serializers | `attrs` | interfaces/serializers/ |
| DTOs (boundary conversion) | `pydantic` | usecases/_dto/ |
| Ports | `typing.Protocol` | usecases/protocols/ |

## Rules

- YAGNI: only create layers and directories as needed
- Value objects: `attrs.frozen(kw_only=True)`
- DTOs: `pydantic.BaseModel` (validation + serialization)
- Ports: `typing.Protocol`
- Concrete classes implementing a Protocol: `*Impl` suffix
- Use-case functions: keyword-only arguments
