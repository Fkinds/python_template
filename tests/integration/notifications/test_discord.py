from http import HTTPStatus
from unittest.mock import patch

import httpx
import pytest

from common.infrastructure.factories.logger import LoggerFactoryImpl
from notifications.infrastructure.adapters.discord import (
    DiscordWebhookNotifierImpl,
)

_TEST_URL = "https://discord.com/api/webhooks/test"
_factory = LoggerFactoryImpl()


class TestDiscordWebhookNotifierImpl:
    """DiscordWebhookNotifierImpl の送信テスト."""

    def test_happy_sends_post_request(self) -> None:
        """Discord Webhook に POST リクエストが送信されること."""
        # Arrange
        notifier = DiscordWebhookNotifierImpl(
            webhook_url=_TEST_URL,
            logger_factory=_factory,
        )
        mock_response = httpx.Response(
            status_code=HTTPStatus.NO_CONTENT,
            request=httpx.Request(
                method="POST",
                url=_TEST_URL,
            ),
        )

        # Act
        with patch.object(
            httpx,
            "post",
            return_value=mock_response,
        ) as mock_post:
            notifier.send(message="テスト通知")

        # Assert
        mock_post.assert_called_once_with(
            url=_TEST_URL,
            json={"content": "テスト通知"},
            timeout=10.0,
        )

    @pytest.mark.parametrize(
        ("exception_cls", "side_effect"),
        [
            (
                httpx.HTTPStatusError,
                None,
            ),
            (
                httpx.TimeoutException,
                httpx.TimeoutException("タイムアウト"),
            ),
            (
                httpx.ConnectError,
                httpx.ConnectError("接続失敗"),
            ),
        ],
        ids=[
            "http_error",
            "timeout",
            "connect_error",
        ],
    )
    def test_error_raises_on_transport_failure(
        self,
        exception_cls: type[Exception],
        side_effect: Exception | None,
    ) -> None:
        """通信障害時に例外が発生すること."""
        # Arrange
        notifier = DiscordWebhookNotifierImpl(
            webhook_url=_TEST_URL,
            logger_factory=_factory,
        )

        if side_effect is not None:
            ctx = patch.object(
                httpx,
                "post",
                side_effect=side_effect,
            )
        else:
            mock_response = httpx.Response(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                request=httpx.Request(
                    method="POST",
                    url=_TEST_URL,
                ),
            )
            ctx = patch.object(
                httpx,
                "post",
                return_value=mock_response,
            )

        # Act & Assert
        with ctx, pytest.raises(exception_cls):
            notifier.send(message="テスト通知")
