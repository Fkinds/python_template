<div align="center">

# fkinds-python

**Web API template project powered by Django REST Framework**

[![CI](https://github.com/Fkinds/python_template/actions/workflows/ci.yml/badge.svg)](https://github.com/Fkinds/python_template/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16-A30000?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Checked with mypy](https://img.shields.io/badge/mypy-strict-blue?logo=python&logoColor=white)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)

</div>

---

## Tech Stack

<table>
<tr>
<td>

| Category | Tools |
|:--|:--|
| **Language** | Python 3.14 |
| **Framework** | Django 5.2 / DRF 3.16 |
| **Database** | PostgreSQL 16 |
| **Object Storage** | RustFS (S3-compatible) |
| **Package Manager** | uv |

</td>
<td>

| Category | Tools |
|:--|:--|
| **Linter / Formatter** | Ruff, Fixit, import-linter |
| **Type Checker** | MyPy (strict), ty |
| **Testing** | pytest, pytest-xdist, Hypothesis |
| **Infrastructure** | Docker, GitHub Actions |

</td>
</tr>
</table>

## Project Structure

```
.
├── src/
│   ├── config/            # Django settings, urls, wsgi, asgi
│   ├── authors/           # Authors app
│   └── books/             # Books app
├── tests/
│   ├── unit/              # Unit tests
│   ├── functional/        # Functional tests (with DB)
│   ├── integration/       # Integration tests
│   └── linting/           # Custom lint rule tests
├── lint_rules/            # Fixit custom rules
├── .github/workflows/     # CI workflows
└── docker-compose.yml
```

## Getting Started

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) 0.10.4+
- Docker / Docker Compose
- Node.js (for commitlint)

### Setup

```bash
# 1. Clone
git clone https://github.com/Fkinds/python_template.git
cd python_template

# 2. Install dependencies
uv sync --dev

# 3. Configure environment
cp .env.example .env   # edit .env as needed

# 4. Start database & object storage
docker compose up -d db rustfs

# 5. Run migrations & create S3 bucket
uv run python src/manage.py migrate
uv run python manage.py ensure_bucket

# 6. Setup git hooks
npm install
uv run pre-commit install

# 7. Start dev server
uv run python src/manage.py runserver
```

> Access the API at `http://localhost:8000`.
> You can also run `docker compose up` to start all services at once.

## Object Storage (RustFS)

[RustFS](https://rustfs.com/) provides S3-compatible object storage
for file uploads (e.g. book cover images).

| Service | URL | Description |
|:--|:--|:--|
| S3 API | `http://localhost:9000` | django-storages endpoint |
| Web Console | `http://localhost:9001` | Browser admin UI |

**Default credentials:** `rustfsadmin` / `rustfsadmin`

```bash
# Create bucket (first time only)
uv run python manage.py ensure_bucket

# Start RustFS standalone
docker compose up -d rustfs
```

## Development

### Code Quality

```bash
uv run ruff check src tests        # Lint
uv run ruff format src tests       # Format
uv run mypy src                    # Type check
uv run fixit lint src tests        # Custom rules
uv run ty check src                # Type check (ty)
```

### Testing

```bash
uv run pytest                              # All tests
uv run pytest tests/unit                   # Unit tests
uv run pytest tests/functional             # Functional tests
uv run pytest tests/integration            # Integration tests
uv run pytest tests/unit --numprocesses auto  # Parallel execution
```

## CI Pipeline

The following jobs run in parallel on push / PR to `main` via GitHub Actions.

| Job | Description |
|:--|:--|
| `ruff` | Lint & format check |
| `fixit` | Custom rule validation |
| `mypy` | Static type check |
| `ty` | Type check |
| `unit_test` | Unit tests (parallel) |
| `functional_test` | Functional tests (PostgreSQL, parallel) |
| `integration_test` | Integration tests (sequential) |
| `commitlint` | Commit message validation |

## Git Convention

Follows [Conventional Commits](https://www.conventionalcommits.org/).

```
<type>: <subject>
```

**Types:** `feat` `fix` `refactor` `test` `chore` `ci` `docs` `revert`

```bash
# Examples
feat: add user authentication endpoint
fix: resolve N+1 query in book list view
```

## Pre-commit Hooks

The following hooks run automatically on each commit.

| Order | Hook | Description |
|:--:|:--|:--|
| 1 | **Ruff** | Lint & format |
| 2 | **MyPy** | Type check |
| 3 | **Fixit** | Custom rules |
| 4 | **pre-commit-hooks** | EOF fix, trailing whitespace |
| 5 | **commitlint** | Commit message validation |
| 6 | **pytest** | Full test suite |
