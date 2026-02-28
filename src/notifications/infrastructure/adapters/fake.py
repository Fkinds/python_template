from __future__ import annotations

from notifications.domain.event_type import EventType
from notifications.domain.notification_channel import NotificationChannel
from notifications.domain.notification_log import NotificationLog
from notifications.domain.notification_status import NotificationStatus


class FakeNotifier:
    """テスト用: 送信メッセージを記録するアダプタ."""

    def __init__(self) -> None:
        self._messages: list[str] = []

    @property
    def messages(self) -> frozenset[str]:
        """記録済みメッセージを不変セットで返す."""
        return frozenset(self._messages)

    def send(self, message: str) -> None:
        """メッセージをリストに記録する."""
        self._messages.append(message)


class FakeNotificationLogWriter:
    """テスト用: 保存された通知履歴を記録するアダプタ."""

    def __init__(self) -> None:
        self._logs: list[dict[str, object]] = []

    @property
    def logs(self) -> list[dict[str, object]]:
        """記録済み通知履歴を返す."""
        return list(self._logs)

    def save(
        self,
        *,
        event_type: EventType,
        message: str,
        status: NotificationStatus,
        detail: str,
        recipient: str,
        channel: NotificationChannel,
        retry_count: int,
    ) -> None:
        """通知履歴を記録する."""
        self._logs.append(
            {
                "event_type": event_type,
                "message": message,
                "status": status,
                "detail": detail,
                "recipient": recipient,
                "channel": channel,
                "retry_count": retry_count,
            }
        )


class FakeNotificationLogReader:
    """テスト用: 固定データを返すリーダーアダプタ."""

    def __init__(self, logs: list[NotificationLog] | None = None) -> None:
        self._logs: list[NotificationLog] = logs if logs is not None else []

    def find_all(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[NotificationLog], int]:
        """固定データの一覧を返す."""
        start = (page - 1) * page_size
        end = start + page_size
        return self._logs[start:end], len(self._logs)

    def find_by_id(self, log_id: str) -> NotificationLog | None:
        """指定IDの固定データを返す."""
        for log in self._logs:
            if log.id == log_id:
                return log
        return None
