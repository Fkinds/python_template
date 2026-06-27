"""共通例外ハンドラ (RFC 9457) のテスト."""

import http
import logging
from typing import Any

import pytest
from django.conf import settings
from rest_framework.exceptions import NotAuthenticated
from rest_framework.test import APIRequestFactory

from common.domain.entities.exceptions import EntityDoesNotExistError
from common.domain.entities.exceptions import EntityError
from common.domain.entities.exceptions import GenerateRepositoryError
from common.domain.exceptions import AppError
from common.infrastructure.adapters.exceptions import AdapterError
from common.infrastructure.exception_handler import custom_exception_handler
from common.infrastructure.factories.exceptions import FactoryError
from common.interfaces.problem_details import PROBLEM_CONTENT_TYPE
from common.interfaces.repositories.exceptions import RepositoryError


def _context(path: str = "/api/test/") -> dict[str, Any]:
    """ハンドラに渡す DRF コンテキストを生成するヘルパー."""
    request = APIRequestFactory().get(path)
    return {"request": request, "view": None, "args": (), "kwargs": {}}


class TestCustomExceptionHandler:
    """custom_exception_handler のテスト."""

    @pytest.mark.parametrize(
        ("exc", "expected_status"),
        [
            (EntityDoesNotExistError(), http.HTTPStatus.NOT_FOUND),
            (EntityError("不正"), http.HTTPStatus.UNPROCESSABLE_ENTITY),
            (
                GenerateRepositoryError("不正"),
                http.HTTPStatus.UNPROCESSABLE_ENTITY,
            ),
            (AdapterError("外部失敗"), http.HTTPStatus.BAD_GATEWAY),
            (FactoryError("依存失敗"), http.HTTPStatus.INTERNAL_SERVER_ERROR),
            (
                RepositoryError("永続失敗"),
                http.HTTPStatus.INTERNAL_SERVER_ERROR,
            ),
            (AppError("未分類"), http.HTTPStatus.INTERNAL_SERVER_ERROR),
        ],
        ids=[
            "not_found",
            "entity_error",
            "generate_repository_error",
            "adapter_error",
            "factory_error",
            "repository_error",
            "unclassified_app_error",
        ],
    )
    def test_happy_maps_app_errors_to_status(
        self,
        exc: Exception,
        expected_status: http.HTTPStatus,
    ) -> None:
        """AppError 配下が想定の HTTP ステータスへ変換されること."""
        # Act
        response = custom_exception_handler(exc, _context())

        # Assert
        assert response.status_code == expected_status
        assert response.data["status"] == int(expected_status)
        assert response.data["type"] == "about:blank"
        assert response.content_type == PROBLEM_CONTENT_TYPE

    def test_happy_client_error_exposes_detail(self) -> None:
        """4xx ではメッセージを detail に含めること."""
        # Act
        response = custom_exception_handler(
            EntityError("不正な値です"),
            _context(),
        )

        # Assert
        assert response.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.data["detail"] == "不正な値です"

    def test_happy_server_error_hides_detail(self) -> None:
        """5xx では内部情報を本体に漏らさないこと."""
        # Act
        response = custom_exception_handler(
            AdapterError("接続失敗の内部詳細"),
            _context(),
        )

        # Assert
        assert response.status_code == http.HTTPStatus.BAD_GATEWAY
        assert response.data["detail"] == ""

    # lint-fixme: ParamLineBreak: 79文字制限で改行が必要
    def test_happy_server_error_is_logged(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """5xx の AppError がサーバ側で記録されること."""
        # Act
        with caplog.at_level(logging.ERROR):
            custom_exception_handler(AdapterError("内部詳細"), _context())

        # Assert
        assert any(
            "サーバ側エラー" in record.getMessage()
            for record in caplog.records
        )

    def test_happy_problem_includes_request_path(self) -> None:
        """instance にリクエストパスが入ること."""
        # Act
        response = custom_exception_handler(
            EntityError("x"),
            _context("/api/foo/?q=1"),
        )

        # Assert
        assert response.data["instance"] == "/api/foo/?q=1"

    def test_happy_delegates_drf_exception(self) -> None:
        """DRF 既定で扱える例外は既定ハンドラに委譲されること."""
        # Act
        response = custom_exception_handler(NotAuthenticated(), _context())

        # Assert
        assert response.status_code == http.HTTPStatus.UNAUTHORIZED
        # 既定ハンドラ経由なので problem+json ではない。
        assert "type" not in response.data

    def test_error_unknown_exception_returns_500(self) -> None:
        """未知の例外でも 500 + 汎用本体を返し、外へ漏らさないこと."""
        # Act
        response = custom_exception_handler(ValueError("想定外"), _context())

        # Assert
        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.data["status"] == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.data["detail"] == ""

    # lint-fixme: ParamLineBreak: 79文字制限で改行が必要
    def test_error_unknown_exception_is_logged(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """未知の例外が握り潰されず記録されること."""
        # Act
        with caplog.at_level(logging.ERROR):
            custom_exception_handler(ValueError("boom"), _context())

        # Assert
        assert any(
            "未処理の例外" in record.getMessage() for record in caplog.records
        )

    def test_happy_handler_registered_in_settings(self) -> None:
        """settings に当ハンドラが登録されていること."""
        # Assert
        assert settings.REST_FRAMEWORK["EXCEPTION_HANDLER"] == (
            "common.infrastructure.exception_handler.custom_exception_handler"
        )
