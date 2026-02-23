from notifications.infrastructure.adapters.fake import FakeNotifier
from notifications.infrastructure.containers.notificaton import (
    NotificationModule,
)
from notifications.infrastructure.containers.notificaton import container
from notifications.usecases.protocols import Notifier
from notifications.usecases.protocols import NotifyAuthorCreatedUseCase
from notifications.usecases.protocols import NotifyBookCreatedUseCase


class TestContainerOverride:
    """DI コンテナの override / reset テスト."""

    def test_happy_override_returns_fake(self) -> None:
        """override で FakeNotifier が返ること."""
        # Arrange
        fake = FakeNotifier()
        container.override(
            NotificationModule(notifier_override=fake),
        )

        # Act
        result = container.injector.get(
            Notifier,  # type: ignore[type-abstract]
        )

        # Assert
        assert result is fake

        # Cleanup
        container.reset()

    def test_happy_default_returns_notifier(self) -> None:
        """デフォルトで Notifier 互換オブジェクトが返ること."""
        # Arrange
        container.reset()

        # Act
        result = container.injector.get(
            Notifier,  # type: ignore[type-abstract]
        )

        # Assert — ConsoleNotifierImpl が返る (dev設定では URL 未設定)
        assert hasattr(result, "send")
        assert callable(result.send)


class TestContainerUseCaseResolution:
    """コンテナからのユースケース解決テスト."""

    def test_happy_book_use_case_satisfies_protocol(
        self,
    ) -> None:
        """NotifyBookCreatedUseCase が Protocol 互換を返すこと."""
        # Arrange
        fake = FakeNotifier()
        container.override(
            NotificationModule(notifier_override=fake),
        )

        # Act
        result = container.injector.get(
            NotifyBookCreatedUseCase,  # type: ignore[type-abstract]
        )

        # Assert
        assert isinstance(result, NotifyBookCreatedUseCase)

        # Cleanup
        container.reset()

    def test_happy_author_use_case_satisfies_protocol(
        self,
    ) -> None:
        """NotifyAuthorCreatedUseCase が Protocol 互換を返すこと."""
        # Arrange
        fake = FakeNotifier()
        container.override(
            NotificationModule(notifier_override=fake),
        )

        # Act
        result = container.injector.get(
            NotifyAuthorCreatedUseCase,  # type: ignore[type-abstract]
        )

        # Assert
        assert isinstance(result, NotifyAuthorCreatedUseCase)

        # Cleanup
        container.reset()
