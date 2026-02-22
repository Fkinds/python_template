from pathlib import Path

import pytest
from fixit.engine import LintRunner
from fixit.ftypes import Config

from lint_rules.param_line_break import ParamLineBreak


@pytest.fixture
def config() -> Config:
    return Config(path=Path("test.py"))


def _lint(
    source: str,
    config: Config,
) -> list[str]:
    runner = LintRunner(config.path, source.encode())
    rule = ParamLineBreak()
    reports = list(runner.collect_violations([rule], config))
    return [r.message for r in reports]


class TestParamLineBreakValid:
    """改行ルールに従っているケースは検出しない"""

    def test_single_param_one_line(self, config: Config) -> None:
        code = "def f(x: int) -> None: ...\n"
        assert _lint(code, config) == []

    def test_self_and_one_param_one_line(self, config: Config) -> None:
        code = (
            "class Foo:\n"
            "    def method(self, x: int) -> None: ...\n"
        )
        assert _lint(code, config) == []

    def test_cls_and_one_param_one_line(self, config: Config) -> None:
        code = (
            "class Foo:\n"
            "    @classmethod\n"
            "    def method(cls, x: int) -> None: ...\n"
        )
        assert _lint(code, config) == []

    def test_multiple_params_with_line_breaks(self, config: Config) -> None:
        code = (
            "def f(\n"
            "    x: int,\n"
            "    y: int,\n"
            ") -> None: ...\n"
        )
        assert _lint(code, config) == []

    def test_self_multi_params_with_breaks(self, config: Config) -> None:
        code = (
            "class Foo:\n"
            "    def method(\n"
            "        self,\n"
            "        x: int,\n"
            "        y: int,\n"
            "    ) -> None: ...\n"
        )
        assert _lint(code, config) == []

    def test_no_params(self, config: Config) -> None:
        code = "def f() -> None: ...\n"
        assert _lint(code, config) == []

    def test_only_self(self, config: Config) -> None:
        code = (
            "class Foo:\n"
            "    def method(self) -> None: ...\n"
        )
        assert _lint(code, config) == []

    def test_star_args_single(self, config: Config) -> None:
        code = "def f(*args: int) -> None: ...\n"
        assert _lint(code, config) == []

    def test_kwargs_single(self, config: Config) -> None:
        code = "def f(**kwargs: int) -> None: ...\n"
        assert _lint(code, config) == []

    def test_kwonly_single(self, config: Config) -> None:
        code = "def f(*, x: int) -> None: ...\n"
        assert _lint(code, config) == []

    def test_self_and_star_args(self, config: Config) -> None:
        code = (
            "class Foo:\n"
            "    def method(self, *args: int) -> None: ...\n"
        )
        assert _lint(code, config) == []

    def test_multiple_with_star_args_line_breaks(self, config: Config) -> None:
        code = (
            "def f(\n"
            "    x: int,\n"
            "    *args: int,\n"
            ") -> None: ...\n"
        )
        assert _lint(code, config) == []

    def test_self_and_kwargs_one_line(self, config: Config) -> None:
        code = (
            "class Foo:\n"
            "    def method(self, **kwargs: int) -> None: ...\n"
        )
        assert _lint(code, config) == []

    def test_self_and_kwonly_one_line(self, config: Config) -> None:
        code = (
            "class Foo:\n"
            "    def method(self, *, x: int) -> None: ...\n"
        )
        assert _lint(code, config) == []

    def test_posonly_single_param(self, config: Config) -> None:
        code = "def f(x: int, /) -> None: ...\n"
        assert _lint(code, config) == []

    def test_async_single_param(self, config: Config) -> None:
        code = "async def f(x: int) -> None: ...\n"
        assert _lint(code, config) == []

    def test_only_self_with_line_break(self, config: Config) -> None:
        code = (
            "class Foo:\n"
            "    def method(\n"
            "        self,\n"
            "    ) -> None: ...\n"
        )
        assert _lint(code, config) == []

    def test_three_params_with_line_breaks(self, config: Config) -> None:
        code = (
            "def f(\n"
            "    x: int,\n"
            "    y: int,\n"
            "    z: int,\n"
            ") -> None: ...\n"
        )
        assert _lint(code, config) == []


class TestParamLineBreakInvalid:
    """改行ルールに違反しているケースを検出する"""

    def test_single_param_with_line_break(self, config: Config) -> None:
        code = (
            "def f(\n"
            "    x: int,\n"
            ") -> None: ...\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "on one line" in messages[0].lower()

    def test_self_and_one_param_with_line_break(self, config: Config) -> None:
        code = (
            "class Foo:\n"
            "    def method(\n"
            "        self,\n"
            "        x: int,\n"
            "    ) -> None: ...\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "on one line" in messages[0].lower()

    def test_multiple_params_no_line_break(self, config: Config) -> None:
        code = "def f(x: int, y: int) -> None: ...\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "line breaks" in messages[0].lower()

    def test_self_multi_params_no_break(self, config: Config) -> None:
        code = (
            "class Foo:\n"
            "    def method(self, x: int, y: int) -> None: ...\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "line breaks" in messages[0].lower()

    def test_three_params_no_line_break(self, config: Config) -> None:
        code = "def f(x: int, y: int, z: int) -> None: ...\n"
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_star_args_and_param_no_line_break(self, config: Config) -> None:
        code = "def f(x: int, *args: int) -> None: ...\n"
        messages = _lint(code, config)
        assert len(messages) == 1

    def test_cls_and_one_param_with_line_break(self, config: Config) -> None:
        code = (
            "class Foo:\n"
            "    @classmethod\n"
            "    def method(\n"
            "        cls,\n"
            "        x: int,\n"
            "    ) -> None: ...\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "on one line" in messages[0].lower()

    def test_star_args_only_with_line_break(self, config: Config) -> None:
        code = (
            "def f(\n"
            "    *args: int,\n"
            ") -> None: ...\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "on one line" in messages[0].lower()

    def test_kwargs_only_with_line_break(self, config: Config) -> None:
        code = (
            "def f(\n"
            "    **kwargs: int,\n"
            ") -> None: ...\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "on one line" in messages[0].lower()

    def test_kwonly_single_with_line_break(self, config: Config) -> None:
        code = (
            "def f(\n"
            "    *,\n"
            "    x: int,\n"
            ") -> None: ...\n"
        )
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "on one line" in messages[0].lower()

    def test_param_and_kwonly_no_line_break(self, config: Config) -> None:
        code = "def f(x: int, *, y: int) -> None: ...\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "line breaks" in messages[0].lower()

    def test_param_and_kwargs_no_line_break(self, config: Config) -> None:
        code = "def f(x: int, **kwargs: int) -> None: ...\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "line breaks" in messages[0].lower()

    def test_posonly_and_regular_no_line_break(self, config: Config) -> None:
        code = "def f(x: int, /, y: int) -> None: ...\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "line breaks" in messages[0].lower()

    def test_async_multiple_params_no_line_break(self, config: Config) -> None:
        code = "async def f(x: int, y: int) -> None: ...\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "line breaks" in messages[0].lower()
