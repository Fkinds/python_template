from pathlib import Path

import pytest
from fixit.engine import LintRunner
from fixit.ftypes import Config

from lint_rules.no_positional_args import NoPositionalArgs


@pytest.fixture
def config() -> Config:
    return Config(path=Path("test.py"))


def _lint(
    source: str,
    config: Config,
) -> list[str]:
    runner = LintRunner(config.path, source.encode())
    rule = NoPositionalArgs()
    reports = list(runner.collect_violations([rule], config))
    return [r.message for r in reports]


class TestNoPositionalArgsValid:
    """キーワード引数を使っているケースは検出しない"""

    def test_first_party_with_keyword_args(self, config: Config) -> None:
        code = (
            "from books.entities.safe_text import SafeText\n"
            "SafeText(value='test')\n"
        )
        assert _lint(code, config) == []

    def test_first_party_class_with_keyword_args(self, config: Config) -> None:
        code = (
            "from books.entities import Book\n"
            "Book(title='test', isbn='1234567890123')\n"
        )
        assert _lint(code, config) == []

    def test_stdlib_with_positional_args(self, config: Config) -> None:
        code = "len([1, 2, 3])\n"
        assert _lint(code, config) == []

    def test_builtin_print(self, config: Config) -> None:
        code = "print('hello')\n"
        assert _lint(code, config) == []

    def test_third_party_with_positional_args(self, config: Config) -> None:
        code = (
            "from rest_framework import serializers\n"
            "serializers.ValidationError('error')\n"
        )
        assert _lint(code, config) == []

    def test_no_args_call(self, config: Config) -> None:
        code = "from books.entities import Book\nBook()\n"
        assert _lint(code, config) == []

    def test_method_call_not_tracked(self, config: Config) -> None:
        code = (
            "from books.entities import Book\n"
            "book = Book(title='test')\n"
            "str(book)\n"
        )
        assert _lint(code, config) == []

    def test_aliased_import_with_keyword(self, config: Config) -> None:
        code = (
            "from books.entities.safe_text import SafeText as ST\n"
            "ST(value='test')\n"
        )
        assert _lint(code, config) == []


class TestNoPositionalArgsInvalid:
    """位置引数を使っているケースを検出する"""

    def test_first_party_positional_arg(self, config: Config) -> None:
        code = (
            "from books.entities.safe_text import SafeText\nSafeText('test')\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "keyword arguments" in messages[0].lower()

    def test_first_party_with_mixed_args(self, config: Config) -> None:
        code = (
            "from books.entities import Book\n"
            "Book('test', isbn='1234567890123')\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_multiple_positional_args(self, config: Config) -> None:
        code = (
            "from books.entities.safe_text import SafeText\n"
            "SafeText('test', 1, 255)\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_aliased_import_with_positional(self, config: Config) -> None:
        code = (
            "from books.entities.safe_text import SafeText as ST\nST('test')\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_authors_module_also_checked(self, config: Config) -> None:
        code = (
            "from authors.serializers import AuthorSerializer\n"
            "AuthorSerializer('data')\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1
