# CLAUDE.md

Django REST Framework API template. Python 3.14 / Django 5.2 / PostgreSQL 16.
Package manager: `uv`. First-party packages: `config`, `common`, `authors`, `books`, `notifications`.

## Rules

- Always prefix commands with `uv run`. Never use bare `python`, `pytest`, or `mypy`.
- Commit with hooks enabled (never use `--no-verify`). If pre-commit fails or is not installed, run manually: `uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src && uv run fixit lint src tests && uv run lint-imports && uv run pytest`
- Business logic belongs in value objects (`entities/`), not in Django models. Models are for persistence only.
- Write test descriptions and business-context comments in Japanese.
- Strictly follow Conventional Commits: `<type>: <subject>` (type: feat|fix|refactor|test|chore|ci|docs|revert, subject: English, lowercase, no period)
- When the user points out an issue and requests a fix, use `git commit --fixup=<target-sha>` instead of a regular commit.

## Code style

- Line length: 79, double quotes, spaces, single-line imports
- Type annotations required (MyPy strict)
- Value objects: `attrs.frozen` + `kw_only=True`
- Models: `auto_now_add` for timestamps, `related_name` on ForeignKey, define `Meta.ordering` and `__str__`
- Serializers: separate by action (list vs detail), set `read_only_fields`
- Implementation classes: Protocol を満たす具象クラスには `*Impl` サフィックスを付ける (例: `NotifierImpl`, `LoggerFactoryImpl`)
- 順序に意味のない定数は `list` ではなく `frozenset` を使う (例: `_ALLOWED = frozenset({"a", "b"})`)
- Tests: Arrange-Act-Assert, prefix `test_happy_` / `test_error_`
