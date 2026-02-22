---
name: create-migration
description: Create and apply Django database migrations. Use when the user modifies models or asks to create migrations.
disable-model-invocation: true
---

Create and apply Django migrations. Always use `uv run`.

## 1. Generate migration files

```bash
uv run python src/manage.py makemigrations
```

## 2. Apply migrations

```bash
uv run python src/manage.py migrate
```

## 3. Check for unapplied migrations

```bash
uv run python src/manage.py showmigrations
```
