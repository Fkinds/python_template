import logging
from http import HTTPStatus

from notifications.domain.events import AuthorCreated
from notifications.domain.events import BookCreated
from notifications.domain.results import NotificationProblem
from notifications.domain.results import NotificationResult
from notifications.domain.results import NotificationSuccess
from notifications.usecases.protocols import Notifier

logger = logging.getLogger(__name__)


class NotifyBookCreatedUseCaseImpl:
    """本作成通知ユースケースの実装."""

    def __init__(self, notifier: Notifier) -> None:
        self._notifier = notifier

    def execute(self, event: BookCreated) -> NotificationResult:
        """本作成イベントの通知を実行する."""
        message = (
            f"本が登録されました: {event.title} (著者: {event.author_name})"
        )
        try:
            self._notifier.send(message=message)
        except Exception:
            logger.warning(
                "本作成通知の送信に失敗: title=%s",
                event.title,
                exc_info=True,
            )
            return NotificationProblem(
                title="Notification Delivery Failed",
                status=HTTPStatus.BAD_GATEWAY,
                detail=(f"本作成通知の送信に失敗しました: {event.title}"),
            )
        logger.info(
            "本作成通知を送信しました: title=%s",
            event.title,
        )
        return NotificationSuccess(message=message)


class NotifyAuthorCreatedUseCaseImpl:
    """著者作成通知ユースケースの実装."""

    def __init__(self, notifier: Notifier) -> None:
        self._notifier = notifier

    def execute(self, event: AuthorCreated) -> NotificationResult:
        """著者作成イベントの通知を実行する."""
        message = f"著者が登録されました: {event.name}"
        try:
            self._notifier.send(message=message)
        except Exception:
            logger.warning(
                "著者作成通知の送信に失敗: name=%s",
                event.name,
                exc_info=True,
            )
            return NotificationProblem(
                title="Notification Delivery Failed",
                status=HTTPStatus.BAD_GATEWAY,
                detail=(f"著者作成通知の送信に失敗しました: {event.name}"),
            )
        logger.info(
            "著者作成通知を送信しました: name=%s",
            event.name,
        )
        return NotificationSuccess(message=message)
