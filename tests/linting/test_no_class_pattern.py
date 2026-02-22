from pathlib import Path

import pytest
from fixit.engine import LintRunner
from fixit.ftypes import Config

from lint_rules.no_class_pattern import NoClassPattern


@pytest.fixture
def config() -> Config:
    return Config(path=Path("test.py"))


def _lint(
    source: str,
    config: Config,
) -> list[str]:
    runner = LintRunner(config.path, source.encode())
    rule = NoClassPattern()
    reports = list(runner.collect_violations([rule], config))
    return [r.message for r in reports]


class TestNoClassPatternValid:
    """クラスパターンを使わないケースは検出しない"""

    def test_literal_pattern(self, config: Config) -> None:
        code = 'match command:\n    case "quit":\n        quit()\n'
        assert _lint(code, config) == []

    def test_sequence_pattern(self, config: Config) -> None:
        code = "match point:\n    case (x, y):\n        print(x, y)\n"
        assert _lint(code, config) == []

    def test_or_pattern(self, config: Config) -> None:
        code = "match value:\n    case 1 | 2 | 3:\n        print('small')\n"
        assert _lint(code, config) == []

    def test_mapping_pattern(self, config: Config) -> None:
        code = (
            'match mapping:\n    case {"key": value}:\n        print(value)\n'
        )
        assert _lint(code, config) == []

    def test_capture_pattern(self, config: Config) -> None:
        code = "match value:\n    case x:\n        print(x)\n"
        assert _lint(code, config) == []

    def test_wildcard_pattern(self, config: Config) -> None:
        code = "match value:\n    case _:\n        pass\n"
        assert _lint(code, config) == []

    def test_guard_with_isinstance(self, config: Config) -> None:
        code = (
            "match point:\n"
            "    case p if isinstance(p, Point):\n"
            "        print(p)\n"
        )
        assert _lint(code, config) == []

    def test_singleton_pattern(self, config: Config) -> None:
        code = (
            "match value:\n"
            "    case None:\n"
            "        pass\n"
            "    case True:\n"
            "        pass\n"
            "    case False:\n"
            "        pass\n"
        )
        assert _lint(code, config) == []

    def test_value_pattern_with_dotted_name(self, config: Config) -> None:
        """Color.RED は MatchValue であり MatchClass ではない"""
        code = (
            "match status:\n"
            "    case Color.RED:\n"
            "        print('red')\n"
            "    case http.HTTPStatus.OK:\n"
            "        print('ok')\n"
        )
        assert _lint(code, config) == []

    def test_as_pattern(self, config: Config) -> None:
        code = "match values:\n    case [1, 2] as pair:\n        print(pair)\n"
        assert _lint(code, config) == []

    def test_star_pattern_in_sequence(self, config: Config) -> None:
        code = (
            "match values:\n    case [first, *rest]:\n        print(first)\n"
        )
        assert _lint(code, config) == []

    def test_function_call_outside_match(self, config: Config) -> None:
        """match 外の通常の関数呼び出しは検出しない"""
        code = "result = Point(1, 2)\n"
        assert _lint(code, config) == []


class TestNoClassPatternInvalid:
    """クラスパターンを検出する"""

    def test_class_with_positional_patterns(self, config: Config) -> None:
        code = "match point:\n    case Point(x, y):\n        print(x, y)\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "class pattern" in messages[0].lower()

    def test_class_with_keyword_patterns(self, config: Config) -> None:
        code = (
            "match color:\n"
            '    case Color(name="red"):\n'
            "        print('red')\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_class_with_no_arguments(self, config: Config) -> None:
        code = "match event:\n    case Quit():\n        quit()\n"
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_nested_class_pattern(self, config: Config) -> None:
        code = (
            "match event:\n"
            "    case Click(position=(x, y)):\n"
            "        handle(x, y)\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_class_pattern_with_dotted_name(self, config: Config) -> None:
        code = (
            "match response:\n"
            "    case http.Response(status=200):\n"
            "        handle()\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_multi_class_patterns_same_match(self, config: Config) -> None:
        code = (
            "match shape:\n"
            "    case Circle(r):\n"
            "        area = 3.14 * r * r\n"
            "    case Rect(w, h):\n"
            "        area = w * h\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 2

    def test_class_pattern_in_or_pattern(self, config: Config) -> None:
        code = (
            "match event:\n"
            "    case Click(x, y) | Drag(x, y):\n"
            "        handle(x, y)\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 2

    def test_builtin_type_pattern(self, config: Config) -> None:
        """int() や str() も MatchClass なので検出する"""
        code = (
            "match value:\n"
            "    case int(x):\n"
            "        print('int', x)\n"
            "    case str(s):\n"
            "        print('str', s)\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 2

    def test_class_pattern_with_guard(self, config: Config) -> None:
        code = (
            "match point:\n"
            "    case Point(x, y) if x > 0:\n"
            "        print(x, y)\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_class_pattern_with_as(self, config: Config) -> None:
        code = "match point:\n    case Point(x, y) as p:\n        print(p)\n"
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_class_pattern_inside_sequence(self, config: Config) -> None:
        code = (
            "match events:\n    case [Click(x, y), _]:\n        handle(x, y)\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_class_pattern_inside_mapping_value(self, config: Config) -> None:
        code = (
            "match data:\n"
            '    case {"event": Click(x, y)}:\n'
            "        handle(x, y)\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1
