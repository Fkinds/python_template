import logging

import httpx

logger = logging.getLogger(__name__)


class DiscordWebhookNotifier:
    """Discord Webhook を使った通知アダプタ."""

    def __init__(self, webhook_url: str) -> None:
        self._webhook_url = webhook_url

    def send(self, message: str) -> None:
        """Discord Webhook にメッセージを送信する."""
        logger.debug(
            "Discord Webhook に送信開始: url=%s",
            self._webhook_url,
        )
        try:
            response = httpx.post(
                url=self._webhook_url,
                json={"content": message},
                timeout=10.0,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.error(
                "Discord Webhook HTTP エラー: url=%s status=%d",
                self._webhook_url,
                response.status_code,
            )
            raise
        except httpx.TransportError:
            logger.error(
                "Discord Webhook 接続エラー: url=%s",
                self._webhook_url,
            )
            raise
        logger.debug(
            "Discord Webhook に送信完了: url=%s",
            self._webhook_url,
        )
