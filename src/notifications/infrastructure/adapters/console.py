import injector

from common.usecases.protocols import LoggerFactory


class ConsoleNotifierImpl:
    """開発環境用: ログに通知内容を出力するアダプタ."""

    @injector.inject
    def __init__(self, logger_factory: LoggerFactory) -> None:
        self._logger = logger_factory.build(name=__name__)

    def send(self, message: str) -> None:
        """ログに通知メッセージを出力する."""
        self._logger.info("[Notification] %s", message)
