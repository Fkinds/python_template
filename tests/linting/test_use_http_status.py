from fixit.engine import LintRunner
from fixit.ftypes import Config

from lint_rules.use_http_status import UseHTTPStatus


def _lint(
    source: str,
    config: Config,
) -> list[str]:
    runner = LintRunner(config.path, source.encode())
    rule = UseHTTPStatus()
    reports = list(runner.collect_violations([rule], config))
    return [r.message for r in reports]


def _autofix(
    source: str,
    config: Config,
) -> str:
    runner = LintRunner(config.path, source.encode())
    rule = UseHTTPStatus()
    reports = list(runner.collect_violations([rule], config))
    return runner.apply_replacements(reports).bytes.decode()


class TestUseHTTPStatusValid:
    """ルールが誤検出しないケース"""

    def test_http_status_enum_is_allowed(self, config: Config) -> None:
        code = (
            "from http import HTTPStatus\n"
            "assert response.status_code == HTTPStatus.OK\n"
        )
        assert _lint(code, config) == []

    def test_non_status_integer_is_allowed(self, config: Config) -> None:
        assert _lint("x = 42\n", config) == []

    def test_large_number_is_allowed(self, config: Config) -> None:
        assert _lint("x = 100_000\n", config) == []

    def test_port_number_is_allowed(self, config: Config) -> None:
        assert _lint("port = 8080\n", config) == []

    def test_max_size_500_is_allowed(self, config: Config) -> None:
        assert _lint("max_size = 500\n", config) == []

    def test_keyword_arg_not_status_is_allowed(self, config: Config) -> None:
        assert _lint("f(max_size=500)\n", config) == []

    def test_timeout_100_is_allowed(self, config: Config) -> None:
        assert _lint("f(timeout=100)\n", config) == []

    def test_positional_arg_is_allowed(self, config: Config) -> None:
        assert _lint("f(200)\n", config) == []

    def test_list_literal_is_allowed(self, config: Config) -> None:
        assert _lint("codes = [200, 404]\n", config) == []

    def test_return_value_is_allowed(self, config: Config) -> None:
        assert _lint("return 200\n", config) == []

    def test_unrelated_variable_name_is_allowed(self, config: Config) -> None:
        assert _lint("data = 200\n", config) == []


class TestUseHTTPStatusInvalid:
    """ルールが検出するケース"""

    def test_comparison_right_side(self, config: Config) -> None:
        code = "assert response.status_code == 200\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "HTTPStatus.OK" in messages[0]

    def test_comparison_left_side(self, config: Config) -> None:
        code = "assert 404 == response.status_code\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "HTTPStatus.NOT_FOUND" in messages[0]

    def test_not_equal_comparison(self, config: Config) -> None:
        code = "response.status_code != 200\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "HTTPStatus.OK" in messages[0]

    def test_gte_comparison(self, config: Config) -> None:
        code = "response.status_code >= 400\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "HTTPStatus.BAD_REQUEST" in messages[0]

    def test_keyword_arg_status(self, config: Config) -> None:
        code = "Response(data, status=200)\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "HTTPStatus.OK" in messages[0]

    def test_keyword_arg_status_code(self, config: Config) -> None:
        code = "f(status_code=201)\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "HTTPStatus.CREATED" in messages[0]

    def test_assignment_to_status_code(self, config: Config) -> None:
        code = "status_code = 500\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "HTTPStatus.INTERNAL_SERVER_ERROR" in messages[0]

    def test_assignment_to_status(self, config: Config) -> None:
        code = "status = 200\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "HTTPStatus.OK" in messages[0]

    def test_assignment_to_http_status(self, config: Config) -> None:
        code = "http_status = 403\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "HTTPStatus.FORBIDDEN" in messages[0]

    def test_if_statement_comparison(self, config: Config) -> None:
        code = "if response.status_code == 200: pass\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "HTTPStatus.OK" in messages[0]

    def test_various_status_codes(self, config: Config) -> None:
        cases = {
            201: "CREATED",
            204: "NO_CONTENT",
            301: "MOVED_PERMANENTLY",
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            404: "NOT_FOUND",
            422: "UNPROCESSABLE_ENTITY",
            500: "INTERNAL_SERVER_ERROR",
            503: "SERVICE_UNAVAILABLE",
        }
        for code_int, enum_name in cases.items():
            messages = _lint(f"response.status_code == {code_int}\n", config)
            assert len(messages) == 1, f"Failed for {code_int}"
            assert f"HTTPStatus.{enum_name}" in messages[0]


class TestUseHTTPStatusAutofix:
    """自動修正のテスト"""

    def test_autofix_comparison(self, config: Config) -> None:
        code = "assert response.status_code == 200\n"
        result = _autofix(code, config)
        assert "http.HTTPStatus.OK" in result
        assert " 200" not in result

    def test_autofix_keyword_arg(self, config: Config) -> None:
        code = "Response(data, status=200)\n"
        result = _autofix(code, config)
        assert "status=http.HTTPStatus.OK" in result

    def test_autofix_assignment(self, config: Config) -> None:
        code = "status_code = 500\n"
        result = _autofix(code, config)
        assert "http.HTTPStatus.INTERNAL_SERVER_ERROR" in result

    def test_autofix_not_equal(self, config: Config) -> None:
        code = "response.status_code != 404\n"
        result = _autofix(code, config)
        assert "http.HTTPStatus.NOT_FOUND" in result
        assert "404" not in result
