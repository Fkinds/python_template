import logging

logger = logging.getLogger(__name__)


class ConsoleNotifier:
    """開発環境用: ログに通知内容を出力するアダプタ."""

    def send(self, message: str) -> None:
        """ログに通知メッセージを出力する."""
        logger.info("[Notification] %s", message)
