---
name: security
description: Security checklist for Django/DRF. Use when implementing authentication, handling user input, working with APIs, or reviewing code for vulnerabilities.
---

# Security Rules

## Input Validation

| Rule | Bad | Good |
|---|---|---|
| Never trust user input | `raw_sql(request.data["id"])` | Use ORM / parameterized queries |
| Validate at system boundaries | Pass raw input to business logic | Validate via serializer first |
| Never use `eval()` / `exec()` on input | `eval(user_expr)` | Use a safe parser or allowlist |

## Django / DRF Specific

| Rule | Bad | Good |
|---|---|---|
| Use ORM; avoid raw SQL | `Model.objects.raw(f"...")` | `Model.objects.filter(pk=id)` |
| Never use `extra()` / `RawSQL()` with user input | `queryset.extra(where=[...])` | ORM lookups / `Q` objects |
| Set `fields` explicitly on serializers | `fields = "__all__"` | `fields = ("id", "name")` |
| Always set `read_only_fields` | Writable auto-generated fields | `read_only_fields = ("id", "created_at")` |
| Use permission classes on every view | No `permission_classes` | `permission_classes = (IsAuthenticated,)` |
| Disable browsable API in production | `DEFAULT_RENDERER_CLASSES` includes browsable | JSON renderer only |

## Secret Management

- Never hardcode secrets, tokens, or passwords in source code
- Use environment variables or a secrets manager
- Never commit `.env`, credentials, or private keys
- Add sensitive files to `.gitignore`

## Dependency Security

- Pin exact versions in `pyproject.toml`
- Audit dependencies regularly (`pip-audit` / `safety`)
- Remove unused dependencies promptly

## Exception Handling (Security)

| Rule | Bad | Good |
|---|---|---|
| Never expose internal errors to users | Return raw traceback in API | Return generic error message |
| Log full details server-side | `pass` in `except` | `logger.exception(...)` |
| Never leak DB schema in responses | `{"error": "column X not found"}` | `{"error": "internal server error"}` |

## Common Anti-Patterns

| Anti-pattern | Risk | Fix |
|---|---|---|
| String formatting in queries | SQL injection | Parameterized queries / ORM |
| `mark_safe()` on user input | XSS | Escape first, or avoid `mark_safe()` |
| `CORS_ALLOW_ALL_ORIGINS = True` | CSRF bypass | Allowlist specific origins |
| `DEBUG = True` in production | Info leakage | Environment-based settings |
| Overly broad URL patterns | Unintended endpoint exposure | Explicit path definitions |
| Missing rate limiting | Brute force / DoS | Use `django-ratelimit` or throttle classes |
