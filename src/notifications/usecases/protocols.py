from typing import Protocol
from typing import runtime_checkable

from notifications.domain.event_type import EventType
from notifications.domain.events import AuthorCreated
from notifications.domain.events import BookCreated
from notifications.domain.notification_channel import NotificationChannel
from notifications.domain.notification_log import NotificationLog
from notifications.domain.notification_status import NotificationStatus
from notifications.domain.results import NotificationResult


@runtime_checkable
class Notifier(Protocol):
    """通知送信のポート."""

    def send(self, message: str) -> None: ...


@runtime_checkable
class NotificationLogWriter(Protocol):
    """通知履歴の書き込みポート."""

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
    ) -> None: ...


@runtime_checkable
class NotificationLogReader(Protocol):
    """通知履歴の読み取りポート."""

    def find_all(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[NotificationLog], int]: ...

    def find_by_id(self, log_id: str) -> NotificationLog | None: ...


@runtime_checkable
class NotifyBookCreatedUseCase(Protocol):
    """本作成通知ユースケースのポート."""

    def execute(self, event: BookCreated) -> NotificationResult: ...


@runtime_checkable
class NotifyAuthorCreatedUseCase(Protocol):
    """著者作成通知ユースケースのポート."""

    def execute(self, event: AuthorCreated) -> NotificationResult: ...


@runtime_checkable
class GetNotificationLogsUseCase(Protocol):
    """通知履歴一覧取得ユースケースのポート."""

    def execute(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[NotificationLog], int]: ...


@runtime_checkable
class GetNotificationLogDetailUseCase(Protocol):
    """通知履歴詳細取得ユースケースのポート."""

    def execute(self, log_id: str) -> NotificationLog | None: ...
