from pathlib import Path

import pytest
from fixit.engine import LintRunner
from fixit.ftypes import Config

from lint_rules.no_attr_shorthand import NoAttrShorthand


@pytest.fixture
def config() -> Config:
    return Config(path=Path("test.py"))


def _lint(
    source: str,
    config: Config,
) -> list[str]:
    runner = LintRunner(config.path, source.encode())
    rule = NoAttrShorthand()
    reports = list(runner.collect_violations([rule], config))
    return [r.message for r in reports]


class TestNoAttrShorthandValid:
    """旧 attr モジュールを使わないケースは検出しない"""

    def test_happy_import_attrs(self, config: Config) -> None:
        """モダンな import attrs は許可"""
        assert _lint("import attrs\n", config) == []

    def test_happy_from_attrs_import(self, config: Config) -> None:
        """from attrs import ... は許可"""
        code = "from attrs import frozen\n"
        assert _lint(code, config) == []

    def test_happy_from_attrs_submodule(self, config: Config) -> None:
        """from attrs.validators import ... は許可"""
        code = "from attrs.validators import instance_of\n"
        assert _lint(code, config) == []

    def test_happy_unrelated_import(self, config: Config) -> None:
        """無関係なモジュールは無視"""
        assert _lint("import json\n", config) == []

    def test_happy_attraction_module(self, config: Config) -> None:
        """attr で始まるが別モジュールは無視"""
        assert _lint("import attraction\n", config) == []

    def test_happy_relative_import(self, config: Config) -> None:
        """相対インポートは module が None なので無視"""
        code = "from . import something\n"
        assert _lint(code, config) == []


class TestNoAttrShorthandInvalid:
    """旧 attr モジュールの使用を検出する"""

    def test_error_import_attr(self, config: Config) -> None:
        """import attr を検出"""
        messages = _lint("import attr\n", config)
        assert len(messages) == 1
        assert "import attrs" in messages[0]

    def test_error_from_attr_import(self, config: Config) -> None:
        """from attr import s を検出"""
        code = "from attr import s\n"
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_error_from_attr_import_attrib(self, config: Config) -> None:
        """from attr import attrib を検出"""
        code = "from attr import attrib\n"
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_error_from_attr_submodule(self, config: Config) -> None:
        """from attr.validators import ... を検出"""
        code = "from attr.validators import instance_of\n"
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_error_import_attr_with_alias(self, config: Config) -> None:
        """import attr as a を検出"""
        code = "import attr as a\n"
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_error_from_attr_star(self, config: Config) -> None:
        """from attr import * を検出"""
        code = "from attr import *\n"
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_error_import_attr_dotted(self, config: Config) -> None:
        """import attr.validators をドット付きで検出"""
        code = "import attr.validators\n"
        messages = _lint(code, config)
        assert len(messages) == 1
