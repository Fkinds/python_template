# Exception Architecture

Design guide for common base exception classes.

## Exception Hierarchy

```
Exception (stdlib)
└── AppError                       # Apex of the pyramid (common/domain)
    ├── EntityError                # Base for entity-related errors
    │   ├── EntityDoesNotExistError    # Entity not found
    │   └── GenerateRepositoryError    # Repository generation failed (see below)
    ├── AdapterError               # Base for adapter-related errors
    │   └── GenerateAdapterError       # Adapter generation failed
    ├── FactoryError               # Base for factory-related errors
    │   └── GenerateFactoryError       # Factory generation failed
    └── RepositoryError            # Base for repository-related errors (reserved)
```

All application exceptions inherit from a single apex `AppError`
(`common/domain/exceptions.py`, stdlib only). A single DRF
`EXCEPTION_HANDLER` (`common/infrastructure/exception_handler.py`) maps
the pyramid to RFC 9457 problem+json, so nothing leaks uncaught and
nothing is silently swallowed.

## HTTP Mapping (exception_handler)

| Exception | HTTP | Notes |
|---|---|---|
| `EntityDoesNotExistError` | 404 | Not found |
| `EntityError` (incl. `GenerateRepositoryError`) | 422 | Invalid entity |
| `AdapterError` | 502 | External service failure |
| `FactoryError` / `RepositoryError` | 500 | Server fault |
| unclassified `AppError` | 500 | Safe default |
| DRF `APIException` | DRF default | Delegated |
| unknown `Exception` | 500 | Caught + logged, generic body |

- 4xx: the exception message is exposed in `detail`.
- 5xx: `detail` is left empty; full error + traceback is logged
  server-side only (no internal leakage).

## Definition Locations

| Directory | base.py | exceptions.py |
|---|---|---|
| `common/domain/` | — | AppError (apex) |
| `common/domain/entities/` | Entity, ValueObject | EntityError, EntityDoesNotExistError, GenerateRepositoryError |
| `common/infrastructure/adapters/` | Adapter | AdapterError, GenerateAdapterError |
| `common/infrastructure/factories/` | Factory | FactoryError, GenerateFactoryError |
| `common/interfaces/repositories/` | Repository | RepositoryError |

## Error Responsibility

Choose the parent class based on **the cause of the error**:

| Cause | Base Class | Example |
|---|---|---|
| Invalid entity passed | `EntityError` | Validation failure, invalid arguments |
| Entity not found | `EntityError` | Lookup with non-existent ID |
| Repository generation failed | `EntityError` | Cannot generate due to invalid entity |
| Network failure / external service error | `AdapterError` | API timeout, connection refused |
| Adapter generation failed | `AdapterError` | Cannot build external client due to misconfiguration |
| Factory generation failed | `FactoryError` | Dependency resolution failure |

### Why GenerateRepositoryError inherits from EntityError

Repository generation failures are most likely caused by
**an invalid entity being passed**. External factors such as
network failures are handled by `AdapterError`. Errors are
classified by the location of the root cause.

## Rules

- All base classes must include an explicit `pass` (PIE790 is disabled)
- Domain-layer exceptions depend on stdlib only (no attrs, no Django)
- Existing `ValueError` in attrs validators must NOT be migrated
  - attrs validators expect `ValueError` / `TypeError`
  - Already converted to `serializers.ValidationError` at the interface layer
