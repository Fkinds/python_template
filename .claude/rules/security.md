# Security Rules

Project-grounded security MUSTs. The example-rich checklist lives
in the `security` skill; this file is the enforced default and
ties the rules to this project's actual architecture.

## 1. Validate at the boundary, first

- Untrusted input is validated by a DRF **deserializer** in
  `interfaces/deserializers/` **before** it reaches usecases or
  domain. Never pass `request.data` into business logic raw.
- Persistence goes through the ORM / parameterized queries. No
  raw SQL, `.extra()`, or `RawSQL()` with user input; no `eval`
  / `exec` / `mark_safe` on input.

## 2. The exception handler is the info-leak barrier

- All errors flow through the single DRF `EXCEPTION_HANDLER`
  (`common/infrastructure/exception_handler.py`). **5xx responses
  never expose `detail`**; the full error + traceback is logged
  server-side only. Do not return raw tracebacks or DB/schema
  strings in responses (see `exception-architecture.md`).

## 3. Serializers expose the minimum

- Set `fields` explicitly (never `"__all__"`) and always declare
  `read_only_fields` for server-owned fields (`id`,
  `created_at`).

## 4. Authentication is out of scope for this template

- This is a **template**: ViewSets intentionally omit
  `permission_classes`, so endpoints are public **by design**.
  Do not cite the template's public views as a pattern.
- When building a real service on this template, add
  `permission_classes` per view (e.g. `IsAuthenticated`) — treat
  the absence as a TODO, not an approval.

## 5. Production hardening

- `DEBUG` is environment-driven and **off** in prod.
- Secrets come from env / a secrets manager (`prod.py` requires
  `SECRET_KEY` with no default); `.env` and keys stay gitignored.
- Restrict renderers in prod to JSON only (disable the DRF
  browsable API): set `DEFAULT_RENDERER_CLASSES` to
  `JSONRenderer` in `prod.py`.
- Allowlist CORS origins (no `CORS_ALLOW_ALL_ORIGINS = True`).

## Rules

- Validate untrusted input at the deserializer boundary before
  usecases; ORM / parameterized only, never raw SQL / `eval` /
  `mark_safe` on input
- 5xx must not leak `detail` / tracebacks / schema — rely on the
  common exception handler; log server-side only
- Serializers: explicit `fields` (no `"__all__"`) +
  `read_only_fields`
- Template omits `permission_classes` by design (auth
  out-of-scope); a real service MUST add per-view permissions
- Prod: `DEBUG` off, env secrets, JSON-only renderer, CORS
  allowlist
