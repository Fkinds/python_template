import httpx

from common.usecases.protocols import LoggerFactory


class DiscordWebhookNotifierImpl:
    """Discord Webhook を使った通知アダプタ."""

    def __init__(
        self,
        webhook_url: str,
        logger_factory: LoggerFactory,
    ) -> None:
        self._webhook_url = webhook_url
        self._logger = logger_factory.build(name=__name__)

    def send(self, message: str) -> None:
        """Discord Webhook にメッセージを送信する."""
        self._logger.debug(
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
            self._logger.error(
                "Discord Webhook HTTP エラー: url=%s status=%d",
                self._webhook_url,
                response.status_code,
            )
            raise
        except httpx.TransportError:
            self._logger.error(
                "Discord Webhook 接続エラー: url=%s",
                self._webhook_url,
            )
            raise
        self._logger.debug(
            "Discord Webhook に送信完了: url=%s",
            self._webhook_url,
        )
