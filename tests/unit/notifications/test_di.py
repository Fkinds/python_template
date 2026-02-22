from notifications.infrastructure.adapters.fake import FakeNotifier
from notifications.infrastructure.containers.notificaton import (
    get_author_created_use_case,
)
from notifications.infrastructure.containers.notificaton import (
    get_book_created_use_case,
)
from notifications.infrastructure.containers.notificaton import get_notifier
from notifications.infrastructure.containers.notificaton import (
    override_notifier,
)
from notifications.usecases.protocols import NotifyAuthorCreatedUseCase
from notifications.usecases.protocols import NotifyBookCreatedUseCase


class TestDiOverride:
    """DI オーバーライド機能のテスト."""

    def test_happy_override_returns_fake(self) -> None:
        """override_notifier で FakeNotifier が返ること."""
        # Arrange
        fake = FakeNotifier()
        override_notifier(notifier=fake)

        # Act
        result = get_notifier()

        # Assert
        assert result is fake

        # Cleanup
        override_notifier(notifier=None)

    def test_happy_default_returns_notifier(self) -> None:
        """デフォルトで Notifier 互換オブジェクトが返ること."""
        # Arrange
        override_notifier(notifier=None)

        # Act
        result = get_notifier()

        # Assert — ConsoleNotifier が返る (dev設定では URL 未設定)
        assert hasattr(result, "send")
        assert callable(result.send)


class TestUseCaseGetters:
    """ユースケース取得ヘルパーのテスト."""

    def test_happy_book_use_case_satisfies_protocol(
        self,
    ) -> None:
        """get_book_created_use_case が Protocol 互換を返すこと."""
        # Arrange
        fake = FakeNotifier()
        override_notifier(notifier=fake)

        # Act
        result = get_book_created_use_case()

        # Assert
        assert isinstance(result, NotifyBookCreatedUseCase)

        # Cleanup
        override_notifier(notifier=None)

    def test_happy_author_use_case_satisfies_protocol(
        self,
    ) -> None:
        """get_author_created_use_case が Protocol 互換を返すこと."""
        # Arrange
        fake = FakeNotifier()
        override_notifier(notifier=fake)

        # Act
        result = get_author_created_use_case()

        # Assert
        assert isinstance(result, NotifyAuthorCreatedUseCase)

        # Cleanup
        override_notifier(notifier=None)
