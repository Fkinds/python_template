import httpx


class DiscordWebhookNotifier:
    """Discord Webhook を使った通知アダプタ."""

    def __init__(self, webhook_url: str) -> None:
        self._webhook_url = webhook_url

    def send(self, message: str) -> None:
        """Discord Webhook にメッセージを送信する."""
        response = httpx.post(
            url=self._webhook_url,
            json={"content": message},
            timeout=10.0,
        )
        response.raise_for_status()
