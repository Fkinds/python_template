"""通知送信ユースケースの実装."""

from http import HTTPStatus

import injector

from common.usecases.protocols import LoggerFactory
from notifications.domain.event_type import EventType
from notifications.domain.events import AuthorCreated
from notifications.domain.events import BookCreated
from notifications.domain.notification_channel import NotificationChannel
from notifications.domain.notification_status import NotificationStatus
from notifications.domain.results import NotificationProblem
from notifications.domain.results import NotificationResult
from notifications.domain.results import NotificationSuccess
from notifications.usecases.protocols import NotificationLogWriter
from notifications.usecases.protocols import Notifier


class NotifyBookCreatedUseCaseImpl:
    """本作成通知ユースケースの実装."""

    @injector.inject
    def __init__(
        self,
        notifier: Notifier,
        logger_factory: LoggerFactory,
        log_writer: NotificationLogWriter,
        channel: NotificationChannel,
    ) -> None:
        self._notifier = notifier
        self._logger = logger_factory.build(name=__name__)
        self._log_writer = log_writer
        self._channel = channel

    def execute(self, event: BookCreated) -> NotificationResult:
        """本作成イベントの通知を実行する."""
        message = (
            f"本が登録されました: {event.title} (著者: {event.author_name})"
        )
        try:
            self._notifier.send(message=message)
        except Exception:
            self._logger.warning(
                "本作成通知の送信に失敗: title=%s",
                event.title,
                exc_info=True,
            )
            self._save_log(
                event_type=EventType.BOOK_CREATED,
                message=message,
                status=NotificationStatus.FAILURE,
                detail=(f"本作成通知の送信に失敗しました: {event.title}"),
            )
            return NotificationProblem(
                title="Notification Delivery Failed",
                status=HTTPStatus.BAD_GATEWAY,
                detail=(f"本作成通知の送信に失敗しました: {event.title}"),
            )
        self._logger.info(
            "本作成通知を送信しました: title=%s",
            event.title,
        )
        self._save_log(
            event_type=EventType.BOOK_CREATED,
            message=message,
            status=NotificationStatus.SUCCESS,
            detail="",
        )
        return NotificationSuccess(message=message)

    def _save_log(
        self,
        *,
        event_type: EventType,
        message: str,
        status: NotificationStatus,
        detail: str,
    ) -> None:
        """通知履歴を保存する (失敗時はログ出力のみ)."""
        try:
            self._log_writer.save(
                event_type=event_type,
                message=message,
                status=status,
                detail=detail,
                recipient=self._channel,
                channel=self._channel,
                retry_count=0,
            )
        except Exception:
            self._logger.warning(
                "通知履歴の保存に失敗: event_type=%s",
                event_type,
                exc_info=True,
            )


class NotifyAuthorCreatedUseCaseImpl:
    """著者作成通知ユースケースの実装."""

    @injector.inject
    def __init__(
        self,
        notifier: Notifier,
        logger_factory: LoggerFactory,
        log_writer: NotificationLogWriter,
        channel: NotificationChannel,
    ) -> None:
        self._notifier = notifier
        self._logger = logger_factory.build(name=__name__)
        self._log_writer = log_writer
        self._channel = channel

    def execute(self, event: AuthorCreated) -> NotificationResult:
        """著者作成イベントの通知を実行する."""
        message = f"著者が登録されました: {event.name}"
        try:
            self._notifier.send(message=message)
        except Exception:
            self._logger.warning(
                "著者作成通知の送信に失敗: name=%s",
                event.name,
                exc_info=True,
            )
            self._save_log(
                event_type=EventType.AUTHOR_CREATED,
                message=message,
                status=NotificationStatus.FAILURE,
                detail=(f"著者作成通知の送信に失敗しました: {event.name}"),
            )
            return NotificationProblem(
                title="Notification Delivery Failed",
                status=HTTPStatus.BAD_GATEWAY,
                detail=(f"著者作成通知の送信に失敗しました: {event.name}"),
            )
        self._logger.info(
            "著者作成通知を送信しました: name=%s",
            event.name,
        )
        self._save_log(
            event_type=EventType.AUTHOR_CREATED,
            message=message,
            status=NotificationStatus.SUCCESS,
            detail="",
        )
        return NotificationSuccess(message=message)

    def _save_log(
        self,
        *,
        event_type: EventType,
        message: str,
        status: NotificationStatus,
        detail: str,
    ) -> None:
        """通知履歴を保存する (失敗時はログ出力のみ)."""
        try:
            self._log_writer.save(
                event_type=event_type,
                message=message,
                status=status,
                detail=detail,
                recipient=self._channel,
                channel=self._channel,
                retry_count=0,
            )
        except Exception:
            self._logger.warning(
                "通知履歴の保存に失敗: event_type=%s",
                event_type,
                exc_info=True,
            )
