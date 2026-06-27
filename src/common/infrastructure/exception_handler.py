"""DRF 共通例外ハンドラ (RFC 9457 problem+json).

例外ピラミッドの頂点 ``AppError`` 配下を、HTTP レスポンスへ単一箇所で
変換する。これにより取りこぼし (未捕捉でのリーク) と握り潰しを防ぐ。

- AppError 系: 種別に応じた status と problem+json
- DRF/Django 既定で扱える例外: 既定ハンドラに委譲
- 未知の例外: 500 + 構造化ログ (内部情報は本体に出さない)

全レイヤの例外型を参照する合成的関心のため、全層を参照できる
infrastructure 層に置く。
"""

import logging
from http import HTTPStatus
from typing import Any

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from common.domain.entities.exceptions import EntityDoesNotExistError
from common.domain.entities.exceptions import EntityError
from common.domain.exceptions import AppError
from common.infrastructure.adapters.exceptions import AdapterError
from common.infrastructure.factories.exceptions import FactoryError
from common.interfaces.problem_details import PROBLEM_CONTENT_TYPE
from common.interfaces.problem_details import build_problem_detail
from common.interfaces.repositories.exceptions import RepositoryError

_logger = logging.getLogger(__name__)


def _map_app_error(exc: AppError) -> tuple[HTTPStatus, str]:
    """AppError 配下を (HTTP ステータス, タイトル) に対応付ける."""
    if isinstance(exc, EntityDoesNotExistError):
        return HTTPStatus.NOT_FOUND, "Not Found"
    if isinstance(exc, EntityError):
        # GenerateRepositoryError を含む。不正なエンティティ起因。
        return HTTPStatus.UNPROCESSABLE_ENTITY, "Unprocessable Entity"
    if isinstance(exc, AdapterError):
        return HTTPStatus.BAD_GATEWAY, "Bad Gateway"
    if isinstance(exc, FactoryError | RepositoryError):
        return HTTPStatus.INTERNAL_SERVER_ERROR, "Internal Server Error"
    # 未分類の AppError 子孫は安全側に倒して 500。
    return HTTPStatus.INTERNAL_SERVER_ERROR, "Internal Server Error"


def _problem_response(
    *,
    status: HTTPStatus,
    title: str,
    detail: str,
    context: dict[str, Any],
) -> Response:
    """problem+json レスポンスを生成する."""
    request = context.get("request")
    instance = request.get_full_path() if request is not None else ""
    body = build_problem_detail(
        status=int(status),
        title=title,
        detail=detail,
        instance=instance,
    )
    return Response(
        body,
        status=int(status),
        content_type=PROBLEM_CONTENT_TYPE,
    )


def custom_exception_handler(
    exc: Exception,
    context: dict[str, Any],
) -> Response:
    """全 API 共通の例外ハンドラ.

    DRF の ``EXCEPTION_HANDLER`` として登録する。未知の例外でも必ず
    Response を返し、500 をそのまま外へ漏らさない (取りこぼし防止)。
    """
    # 1. DRF/Django が扱える例外 (ValidationError 等) は既定に委譲。
    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    # 2. アプリ例外 (AppError ピラミッド) を problem+json へ。
    if isinstance(exc, AppError):
        status, title = _map_app_error(exc)
        if status >= HTTPStatus.INTERNAL_SERVER_ERROR:
            # サーバ側障害: 追跡可能にしつつ内部情報は本体に出さない。
            # except 文脈外から呼ばれても traceback が残るよう exc_info 明示。
            _logger.error(
                "サーバ側エラー: %s",
                type(exc).__name__,
                exc_info=exc,
            )
            detail = ""
        else:
            # クライアント起因: メッセージは安全なので返す。
            _logger.info("クライアントエラー: %s", type(exc).__name__)
            detail = str(exc)
        return _problem_response(
            status=status,
            title=title,
            detail=detail,
            context=context,
        )

    # 3. 未知の例外: 取りこぼし防止。500 + 構造化ログ (本体は汎用)。
    _logger.error(
        "未処理の例外: %s",
        type(exc).__name__,
        exc_info=exc,
    )
    return _problem_response(
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
        title="Internal Server Error",
        detail="",
        context=context,
    )
