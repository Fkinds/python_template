from typing import Protocol
from typing import runtime_checkable

from notifications.domain.events import AuthorCreated
from notifications.domain.events import BookCreated


@runtime_checkable
class Notifier(Protocol):
    """通知送信のポート."""

    def send(self, message: str) -> None:
        """メッセージを送信する."""
        ...


@runtime_checkable
class NotifyBookCreatedUseCase(Protocol):
    """本作成通知ユースケースのポート."""

    def execute(self, event: BookCreated) -> None:
        """本作成イベントの通知を実行する."""
        ...


@runtime_checkable
class NotifyAuthorCreatedUseCase(Protocol):
    """著者作成通知ユースケースのポート."""

    def execute(self, event: AuthorCreated) -> None:
        """著者作成イベントの通知を実行する."""
        ...
