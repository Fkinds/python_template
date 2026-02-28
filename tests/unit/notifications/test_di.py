from notifications.domain.notification_channel import NotificationChannel
from notifications.infrastructure.adapters.fake import (
    FakeNotificationLogReader,
)
from notifications.infrastructure.adapters.fake import (
    FakeNotificationLogWriter,
)
from notifications.infrastructure.adapters.fake import FakeNotifier
from notifications.infrastructure.containers.notificaton import (
    NotificationModule,
)
from notifications.infrastructure.containers.notificaton import container
from notifications.usecases.protocols import GetNotificationLogDetailUseCase
from notifications.usecases.protocols import GetNotificationLogsUseCase
from notifications.usecases.protocols import Notifier
from notifications.usecases.protocols import NotifyAuthorCreatedUseCase
from notifications.usecases.protocols import NotifyBookCreatedUseCase


def _override_with_fakes() -> None:
    """テスト用の Fake をすべて DI に差し込む."""
    container.override(
        NotificationModule(
            notifier_override=FakeNotifier(),
            log_writer_override=(FakeNotificationLogWriter()),
            log_reader_override=(FakeNotificationLogReader()),
            channel_override=NotificationChannel.FAKE,
        ),
    )


class TestContainerOverride:
    """DI コンテナの override / reset テスト."""

    def test_happy_override_returns_fake(
        self,
    ) -> None:
        """override で FakeNotifier が返ること."""
        # Arrange
        fake = FakeNotifier()
        container.override(
            NotificationModule(
                notifier_override=fake,
                log_writer_override=(FakeNotificationLogWriter()),
                log_reader_override=(FakeNotificationLogReader()),
            ),
        )

        # Act
        result = container.injector.get(
            Notifier,  # type: ignore[type-abstract]
        )

        # Assert
        assert result is fake

        # Cleanup
        container.reset()

    def test_happy_default_returns_notifier(
        self,
    ) -> None:
        """デフォルトで Notifier 互換オブジェクトが返ること."""
        # Arrange
        container.reset()

        # Act
        result = container.injector.get(
            Notifier,  # type: ignore[type-abstract]
        )

        # Assert
        assert hasattr(result, "send")
        assert callable(result.send)


class TestContainerUseCaseResolution:
    """コンテナからのユースケース解決テスト."""

    def test_happy_book_use_case_satisfies_protocol(
        self,
    ) -> None:
        """NotifyBookCreatedUseCase が Protocol 互換を返すこと."""
        # Arrange
        _override_with_fakes()

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
        _override_with_fakes()

        # Act
        result = container.injector.get(
            NotifyAuthorCreatedUseCase,  # type: ignore[type-abstract]
        )

        # Assert
        assert isinstance(result, NotifyAuthorCreatedUseCase)

        # Cleanup
        container.reset()

    def test_happy_get_logs_use_case_resolves(
        self,
    ) -> None:
        """GetNotificationLogsUseCase が解決されること."""
        # Arrange
        _override_with_fakes()

        # Act
        result = container.injector.get(
            GetNotificationLogsUseCase,  # type: ignore[type-abstract]
        )

        # Assert
        assert isinstance(result, GetNotificationLogsUseCase)

        # Cleanup
        container.reset()

    def test_happy_get_log_detail_use_case_resolves(
        self,
    ) -> None:
        """GetNotificationLogDetailUseCase が解決されること."""
        # Arrange
        _override_with_fakes()

        # Act
        result = container.injector.get(
            GetNotificationLogDetailUseCase,  # type: ignore[type-abstract]
        )

        # Assert
        assert isinstance(result, GetNotificationLogDetailUseCase)

        # Cleanup
        container.reset()
