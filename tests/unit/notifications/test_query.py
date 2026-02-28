from datetime import UTC
from datetime import datetime

from notifications.domain.event_type import EventType
from notifications.domain.notification_channel import NotificationChannel
from notifications.domain.notification_log import NotificationLog
from notifications.domain.notification_status import NotificationStatus
from notifications.infrastructure.adapters.fake import (
    FakeNotificationLogReader,
)
from notifications.usecases.query import GetNotificationLogDetailUseCaseImpl
from notifications.usecases.query import GetNotificationLogsUseCaseImpl


def _make_log(log_id: str = "abc") -> NotificationLog:
    """テスト用の NotificationLog を生成するヘルパー."""
    return NotificationLog(
        id=log_id,
        event_type=EventType.BOOK_CREATED,
        message="本が登録されました: テスト",
        status=NotificationStatus.SUCCESS,
        detail="",
        recipient="discord",
        channel=NotificationChannel.DISCORD,
        retry_count=0,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


class TestGetNotificationLogsUseCaseImpl:
    """通知履歴一覧取得ユースケースのテスト."""

    def test_happy_returns_list_and_count(self) -> None:
        """履歴一覧とカウントが返ること."""
        # Arrange
        logs = [_make_log(log_id=f"id-{i}") for i in range(3)]
        reader = FakeNotificationLogReader(logs=logs)
        use_case = GetNotificationLogsUseCaseImpl(
            reader=reader,
        )

        # Act
        result, total = use_case.execute(page=1, page_size=10)

        # Assert
        assert len(result) == 3
        assert total == 3

    def test_happy_empty_list(self) -> None:
        """履歴がない場合に空リストが返ること."""
        # Arrange
        reader = FakeNotificationLogReader(logs=[])
        use_case = GetNotificationLogsUseCaseImpl(
            reader=reader,
        )

        # Act
        result, total = use_case.execute(page=1, page_size=10)

        # Assert
        assert result == []
        assert total == 0

    def test_happy_pagination(self) -> None:
        """ページネーションが正しく動作すること."""
        # Arrange
        logs = [_make_log(log_id=f"id-{i}") for i in range(5)]
        reader = FakeNotificationLogReader(logs=logs)
        use_case = GetNotificationLogsUseCaseImpl(
            reader=reader,
        )

        # Act
        page1, total = use_case.execute(page=1, page_size=2)
        page2, _ = use_case.execute(page=2, page_size=2)
        page3, _ = use_case.execute(page=3, page_size=2)

        # Assert
        assert total == 5
        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1


class TestGetNotificationLogDetailUseCaseImpl:
    """通知履歴詳細取得ユースケースのテスト."""

    def test_happy_returns_entity(self) -> None:
        """指定IDの履歴が返ること."""
        # Arrange
        log = _make_log(log_id="target-id")
        reader = FakeNotificationLogReader(logs=[log])
        use_case = GetNotificationLogDetailUseCaseImpl(
            reader=reader,
        )

        # Act
        result = use_case.execute(log_id="target-id")

        # Assert
        assert result is not None
        assert result.id == "target-id"

    def test_happy_returns_none_when_not_found(
        self,
    ) -> None:
        """存在しないIDの場合にNoneが返ること."""
        # Arrange
        reader = FakeNotificationLogReader(logs=[])
        use_case = GetNotificationLogDetailUseCaseImpl(
            reader=reader,
        )

        # Act
        result = use_case.execute(log_id="nonexistent")

        # Assert
        assert result is None
