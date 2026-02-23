from fixit.engine import LintRunner
from fixit.ftypes import Config

from lint_rules.attrs_kw_only import AttrsKwOnly


def _lint(
    source: str,
    config: Config,
) -> list[str]:
    runner = LintRunner(config.path, source.encode())
    rule = AttrsKwOnly()
    reports = list(runner.collect_violations([rule], config))
    return [r.message for r in reports]


class TestAttrsKwOnlyValid:
    """kw_only=True が指定されたケースは検出しない"""

    def test_frozen_with_kw_only(self, config: Config) -> None:
        code = (
            "import attrs\n"
            "@attrs.frozen(kw_only=True)\n"
            "class Foo:\n"
            "    x: int = 1\n"
        )
        assert _lint(code, config) == []

    def test_define_with_kw_only(self, config: Config) -> None:
        code = (
            "import attrs\n"
            "@attrs.define(kw_only=True)\n"
            "class Foo:\n"
            "    x: int = 1\n"
        )
        assert _lint(code, config) == []

    def test_frozen_with_kw_only_and_other_args(self, config: Config) -> None:
        code = (
            "import attrs\n"
            "@attrs.frozen(slots=True, kw_only=True)\n"
            "class Foo:\n"
            "    x: int = 1\n"
        )
        assert _lint(code, config) == []

    def test_non_attrs_decorator_ignored(self, config: Config) -> None:
        code = (
            "from dataclasses import dataclass\n"
            "@dataclass\n"
            "class Foo:\n"
            "    x: int = 1\n"
        )
        assert _lint(code, config) == []

    def test_plain_class_ignored(self, config: Config) -> None:
        code = "class Foo:\n    x: int = 1\n"
        assert _lint(code, config) == []


class TestAttrsKwOnlyInvalid:
    """kw_only=True がないケースを検出する"""

    def test_frozen_bare(self, config: Config) -> None:
        code = "import attrs\n@attrs.frozen\nclass Foo:\n    x: int = 1\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "kw_only=True" in messages[0]

    def test_frozen_empty_parens(self, config: Config) -> None:
        code = "import attrs\n@attrs.frozen()\nclass Foo:\n    x: int = 1\n"
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_define_bare(self, config: Config) -> None:
        code = "import attrs\n@attrs.define\nclass Foo:\n    x: int = 1\n"
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_define_empty_parens(self, config: Config) -> None:
        code = "import attrs\n@attrs.define()\nclass Foo:\n    x: int = 1\n"
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_frozen_other_args_no_kw_only(self, config: Config) -> None:
        code = (
            "import attrs\n"
            "@attrs.frozen(slots=True)\n"
            "class Foo:\n"
            "    x: int = 1\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_frozen_with_kw_only_false(self, config: Config) -> None:
        code = (
            "import attrs\n"
            "@attrs.frozen(kw_only=False)\n"
            "class Foo:\n"
            "    x: int = 1\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1
