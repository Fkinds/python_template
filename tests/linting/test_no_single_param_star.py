from pathlib import Path

import pytest
from fixit.engine import LintRunner
from fixit.ftypes import Config

from lint_rules.no_single_param_star import NoSingleParamStar


@pytest.fixture
def config() -> Config:
    return Config(path=Path("test.py"))


def _lint(
    source: str,
    config: Config,
) -> list[str]:
    runner = LintRunner(config.path, source.encode())
    rule = NoSingleParamStar()
    reports = list(runner.collect_violations([rule], config))
    return [r.message for r in reports]


class TestNoSingleParamStarValid:
    """* が意味を持つケースは検出しない."""

    def test_happy_no_star(self, config: Config) -> None:
        """star なしの通常メソッドは無視すること."""
        code = "def foo(self, a: int) -> None: ...\n"
        assert _lint(code, config) == []

    def test_happy_multiple_kw_only(self, config: Config) -> None:
        """kw-only パラメータが複数なら許可すること."""
        code = "def foo(self, *, a: int, b: str) -> None: ...\n"
        assert _lint(code, config) == []

    def test_happy_positional_and_kw_only(self, config: Config) -> None:
        """positional + kw-only の分離は許可すること."""
        code = "def foo(a: int, *, b: str) -> None: ...\n"
        assert _lint(code, config) == []

    def test_happy_star_args(self, config: Config) -> None:
        """*args は bare * ではないので無視すること."""
        code = "def foo(*args: int) -> None: ...\n"
        assert _lint(code, config) == []

    def test_happy_no_params(self, config: Config) -> None:
        """パラメータなしの関数は無視すること."""
        code = "def foo() -> None: ...\n"
        assert _lint(code, config) == []


class TestNoSingleParamStarInvalid:
    """単一パラメータで * を使うケースを検出する."""

    def test_error_method_single_kw_only(self, config: Config) -> None:
        """メソッドの単一 kw-only パラメータを検出すること."""
        code = "def foo(self, *, msg: str) -> None: ...\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "Remove" in messages[0]

    def test_error_function_single_kw_only(self, config: Config) -> None:
        """関数の単一 kw-only パラメータを検出すること."""
        code = "def foo(*, msg: str) -> None: ...\n"
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_error_cls_single_kw_only(self, config: Config) -> None:
        """クラスメソッドの単一 kw-only パラメータを検出すること."""
        code = "def foo(cls, *, msg: str) -> None: ...\n"
        messages = _lint(code, config)
        assert len(messages) == 1
