"""RFC 9457 Problem Details の生成.

References
----------
https://www.rfc-editor.org/rfc/rfc9457
"""

from typing import TypedDict

PROBLEM_CONTENT_TYPE = "application/problem+json"


class ProblemDetail(TypedDict):
    """RFC 9457 problem 本体の型."""

    type: str
    title: str
    status: int
    detail: str
    instance: str


def build_problem_detail(
    *,
    status: int,
    title: str,
    detail: str = "",
    type_uri: str = "about:blank",
    instance: str = "",
) -> ProblemDetail:
    """RFC 9457 準拠の problem 本体を組み立てる."""
    return {
        "type": type_uri,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance,
    }
