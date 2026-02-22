import logging

import pytest

from notifications.infrastructure.adapters.console import ConsoleNotifier

type LogFixture = pytest.LogCaptureFixture


class TestConsoleNotifier:
    """ConsoleNotifier のログ出力テスト."""

    def test_happy_logs_message(self, caplog: LogFixture) -> None:
        """通知メッセージがログに出力されること."""
        # Arrange
        notifier = ConsoleNotifier()

        # Act
        with caplog.at_level(logging.INFO):
            notifier.send(message="テスト通知")

        # Assert
        assert "[Notification] テスト通知" in caplog.text
