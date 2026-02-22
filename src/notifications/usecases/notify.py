from notifications.domain.events import AuthorCreated
from notifications.domain.events import BookCreated
from notifications.usecases.protocols import Notifier


class NotifyBookCreatedUseCaseImpl:
    """本作成通知ユースケースの実装."""

    def __init__(self, notifier: Notifier) -> None:
        self._notifier = notifier

    def execute(self, event: BookCreated) -> None:
        """本作成イベントの通知を実行する."""
        self._notifier.send(
            message=(
                "本が登録されました:"
                f" {event.title}"
                f" (著者: {event.author_name})"
            ),
        )


class NotifyAuthorCreatedUseCaseImpl:
    """著者作成通知ユースケースの実装."""

    def __init__(self, notifier: Notifier) -> None:
        self._notifier = notifier

    def execute(self, event: AuthorCreated) -> None:
        """著者作成イベントの通知を実行する."""
        self._notifier.send(
            message=f"著者が登録されました: {event.name}",
        )
