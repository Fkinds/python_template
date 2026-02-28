"""通知履歴参照ユースケースの実装."""

import injector

from notifications.domain.notification_log import NotificationLog
from notifications.usecases.protocols import NotificationLogReader


class GetNotificationLogsUseCaseImpl:
    """通知履歴一覧取得ユースケースの実装."""

    @injector.inject
    def __init__(self, reader: NotificationLogReader) -> None:
        self._reader = reader

    def execute(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[NotificationLog], int]:
        """通知履歴の一覧を取得する."""
        return self._reader.find_all(
            page=page,
            page_size=page_size,
        )


class GetNotificationLogDetailUseCaseImpl:
    """通知履歴詳細取得ユースケースの実装."""

    @injector.inject
    def __init__(self, reader: NotificationLogReader) -> None:
        self._reader = reader

    def execute(self, log_id: str) -> NotificationLog | None:
        """指定IDの通知履歴を取得する."""
        return self._reader.find_by_id(log_id=log_id)
