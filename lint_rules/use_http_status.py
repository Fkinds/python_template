import libcst as cst
from fixit import Invalid
from fixit import LintRule
from fixit import Valid

HTTP_STATUS_CODES: dict[int, str] = {
    100: "CONTINUE",
    101: "SWITCHING_PROTOCOLS",
    200: "OK",
    201: "CREATED",
    202: "ACCEPTED",
    204: "NO_CONTENT",
    301: "MOVED_PERMANENTLY",
    302: "FOUND",
    303: "SEE_OTHER",
    304: "NOT_MODIFIED",
    307: "TEMPORARY_REDIRECT",
    308: "PERMANENT_REDIRECT",
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    406: "NOT_ACCEPTABLE",
    408: "REQUEST_TIMEOUT",
    409: "CONFLICT",
    410: "GONE",
    415: "UNSUPPORTED_MEDIA_TYPE",
    422: "UNPROCESSABLE_ENTITY",
    429: "TOO_MANY_REQUESTS",
    500: "INTERNAL_SERVER_ERROR",
    501: "NOT_IMPLEMENTED",
    502: "BAD_GATEWAY",
    503: "SERVICE_UNAVAILABLE",
    504: "GATEWAY_TIMEOUT",
}


def _make_replacement(enum_name: str) -> cst.Attribute:
    return cst.Attribute(
        value=cst.Attribute(
            value=cst.Name("http"),
            attr=cst.Name("HTTPStatus"),
        ),
        attr=cst.Name(enum_name),
    )


def _check_integer(
    node: cst.Integer,
) -> tuple[int, str] | None:
    try:
        value = int(node.value)
    except ValueError:
        return None
    if value not in HTTP_STATUS_CODES:
        return None
    return value, HTTP_STATUS_CODES[value]


class UseHTTPStatus(LintRule):
    """
    Detect raw integer HTTP status codes in comparisons and
    status-related keyword arguments, and suggest using
    ``http.HTTPStatus`` enum members instead.

    Only flags integers in contexts likely to be HTTP status codes:
    comparisons (``== 200``), keyword arguments named ``status``
    or ``status_code``, and assignments to variables containing
    ``status``.
    """

    MESSAGE = "Use `http.HTTPStatus` instead of raw integer status codes."

    VALID = [
        Valid(
            "from http import HTTPStatus\n"
            "assert response.status_code == HTTPStatus.OK"
        ),
        Valid("x = 42"),
        Valid("x = 100_000"),
        Valid("port = 8080"),
        Valid("max_size = 500"),
        Valid("f(max_size=500)"),
        Valid("f(timeout=100)"),
    ]
    INVALID = [
        Invalid(
            "assert response.status_code == 200",
            expected_replacement=(
                "assert response.status_code == http.HTTPStatus.OK"
            ),
        ),
        Invalid(
            "assert 404 == response.status_code",
            expected_replacement=(
                "assert http.HTTPStatus.NOT_FOUND == response.status_code"
            ),
        ),
        Invalid(
            "Response(data, status=200)",
            expected_replacement=("Response(data, status=http.HTTPStatus.OK)"),
        ),
        Invalid(
            "status_code = 500",
            expected_replacement=(
                "status_code = http.HTTPStatus.INTERNAL_SERVER_ERROR"
            ),
        ),
    ]

    def _report_integer(
        self, node: cst.Integer, value: int, enum_name: str
    ) -> None:
        self.report(
            node,
            f"Use `http.HTTPStatus.{enum_name}` instead of `{value}`.",
            replacement=_make_replacement(enum_name),
        )

    def visit_Comparison(self, node: cst.Comparison) -> None:
        # Left side: 200 == response.status_code
        if isinstance(node.left, cst.Integer):
            result = _check_integer(node.left)
            if result:
                self._report_integer(node.left, *result)

        # Right side(s): response.status_code == 200
        for target in node.comparisons:
            if isinstance(target.comparator, cst.Integer):
                result = _check_integer(target.comparator)
                if result:
                    self._report_integer(target.comparator, *result)

    def visit_Arg(self, node: cst.Arg) -> None:
        # Keyword arguments: Response(status=200)
        if (
            node.keyword is not None
            and node.keyword.value in ("status", "status_code")
            and isinstance(node.value, cst.Integer)
        ):
            result = _check_integer(node.value)
            if result:
                self._report_integer(node.value, *result)

    def visit_Assign(self, node: cst.Assign) -> None:
        # Assignments: status_code = 200
        if not isinstance(node.value, cst.Integer):
            return
        result = _check_integer(node.value)
        if not result:
            return
        for target in node.targets:
            name = target.target
            if isinstance(name, cst.Name) and "status" in name.value:
                self._report_integer(node.value, *result)
                return
