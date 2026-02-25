# Exception Architecture

Design guide for common base exception classes.

## Exception Hierarchy

```
Exception (stdlib)
├── EntityError                    # Base for entity-related errors
│   ├── EntityDoesNotExistError    # Entity not found
│   └── GenerateRepositoryError    # Repository generation failed (see below)
├── AdapterError                   # Base for adapter-related errors
│   └── GenerateAdapterError       # Adapter generation failed
├── FactoryError                   # Base for factory-related errors
│   └── GenerateFactoryError       # Factory generation failed
└── RepositoryError                # Base for repository-related errors (reserved)
```

## Definition Locations

| Directory | base.py | exceptions.py |
|---|---|---|
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
