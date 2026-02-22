from http import HTTPStatus

import attrs


@attrs.frozen(kw_only=True)
class NotificationSuccess:
    """通知送信が成功したことを表す結果値オブジェクト.

    RFC 9110 HTTP Semantics に基づき status を保持する。

    References
    ----------
    https://www.rfc-editor.org/rfc/rfc9110#section-15
    """

    status: int = HTTPStatus.OK
    message: str = ""


@attrs.frozen(kw_only=True)
class NotificationProblem:
    """RFC 9457 Problem Details に準拠した通知エラー値オブジェクト.

    References
    ----------
    https://www.rfc-editor.org/rfc/rfc9457
    """

    type_uri: str = "about:blank"
    title: str = ""
    status: int = 0
    detail: str = ""
    instance: str = ""


NotificationResult = NotificationSuccess | NotificationProblem
