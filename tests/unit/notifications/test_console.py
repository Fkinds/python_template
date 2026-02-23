import logging
from unittest.mock import create_autospec

from common.usecases.protocols import LoggerFactory
from notifications.infrastructure.adapters.console import ConsoleNotifierImpl


class _StubLoggerFactory:
    """テスト用: 固定の mock Logger を返すファクトリ."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def build(self, name: str) -> logging.Logger:
        return self._logger


class TestConsoleNotifierImpl:
    """ConsoleNotifierImpl のログ出力テスト."""

    def test_happy_logs_message(self) -> None:
        """通知メッセージがログに出力されること."""
        # Arrange
        mock_logger = create_autospec(
            logging.Logger,
            instance=True,
        )
        factory: LoggerFactory = _StubLoggerFactory(mock_logger)
        notifier = ConsoleNotifierImpl(logger_factory=factory)

        # Act
        notifier.send(message="テスト通知")

        # Assert
        mock_logger.info.assert_called_once_with(
            "[Notification] %s",
            "テスト通知",
        )
