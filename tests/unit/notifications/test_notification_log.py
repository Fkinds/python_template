import uuid
from datetime import UTC
from datetime import datetime

import pytest

from notifications.domain.event_type import EventType
from notifications.domain.notification_channel import NotificationChannel
from notifications.domain.notification_log import NotificationLog
from notifications.domain.notification_status import NotificationStatus

_VALID_ID = uuid.UUID("0192f0a0-0000-7000-8000-000000000001")


def _valid_log(**overrides: object) -> NotificationLog:
    """テスト用の有効な NotificationLog を生成するヘルパー."""
    defaults: dict[str, object] = {
        "id": _VALID_ID,
        "event_type": EventType.BOOK_CREATED,
        "message": "本が登録されました: テスト",
        "status": NotificationStatus.SUCCESS,
        "detail": "",
        "recipient": "discord",
        "channel": NotificationChannel.DISCORD,
        "retry_count": 0,
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    defaults.update(overrides)
    # id=None を渡したときは省略し、基底クラスの uuid7 自動採番に委ねる。
    if defaults.get("id", _VALID_ID) is None:
        del defaults["id"]
    return NotificationLog(**defaults)  # type: ignore[arg-type]


class TestNotificationLog:
    """NotificationLog ドメインエンティティのテスト."""

    def test_happy_create_notification_log(self) -> None:
        """全フィールドを指定して正常に生成されること."""
        # Arrange
        now = datetime(2026, 1, 1, tzinfo=UTC)

        # Act
        log = NotificationLog(
            id=_VALID_ID,
            event_type=EventType.BOOK_CREATED,
            message="本が登録されました: テスト",
            status=NotificationStatus.SUCCESS,
            detail="",
            recipient="discord",
            channel=NotificationChannel.DISCORD,
            retry_count=0,
            created_at=now,
        )

        # Assert
        assert log.id == _VALID_ID
        assert log.event_type == EventType.BOOK_CREATED
        assert log.message == "本が登録されました: テスト"
        assert log.status == NotificationStatus.SUCCESS
        assert log.detail == ""
        assert log.recipient == "discord"
        assert log.channel == NotificationChannel.DISCORD
        assert log.retry_count == 0
        assert log.created_at == now

    def test_happy_failure_status(self) -> None:
        """failure ステータスで生成できること."""
        # Act
        log = _valid_log(
            status=NotificationStatus.FAILURE,
            detail="送信に失敗しました",
        )

        # Assert
        assert log.status == NotificationStatus.FAILURE
        assert log.detail == "送信に失敗しました"

    @pytest.mark.parametrize(
        "channel",
        list(NotificationChannel),
        ids=[c.value for c in NotificationChannel],
    )
    def test_happy_valid_channels(self, channel: NotificationChannel) -> None:
        """有効なチャネル値で生成できること."""
        # Act
        log = _valid_log(channel=channel, recipient=channel)

        # Assert
        assert log.channel == channel

    def test_error_rejects_invalid_status(self) -> None:
        """不正な status が拒否されること."""
        # Act & Assert
        with pytest.raises(ValueError, match="NotificationStatus"):
            _valid_log(status="unknown")

    def test_error_rejects_invalid_channel(
        self,
    ) -> None:
        """不正な channel が拒否されること."""
        # Act & Assert
        with pytest.raises(ValueError, match="NotificationChannel"):
            _valid_log(channel="slack")

    def test_happy_auto_generates_uuid_id(self) -> None:
        """id を省略すると uuid7 が自動採番されること."""
        # Act
        log1 = _valid_log(id=None)
        log2 = _valid_log(id=None)

        # Assert
        assert isinstance(log1.id, uuid.UUID)
        assert log1.id != log2.id

    def test_error_rejects_non_uuid_id(self) -> None:
        """UUID 以外の id が拒否されること."""
        # Act & Assert
        with pytest.raises(TypeError, match="id"):
            _valid_log(id="not-a-uuid")

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("message", ""),
            ("message", "\t"),
            ("recipient", ""),
            ("recipient", " "),
        ],
        ids=[
            "empty_message",
            "blank_message",
            "empty_recipient",
            "blank_recipient",
        ],
    )
    def test_error_rejects_empty_or_blank_field(
        self,
        field: str,
        value: str,
    ) -> None:
        """空文字・空白のみのフィールドが拒否されること."""
        # Act & Assert
        with pytest.raises(ValueError, match=field):
            _valid_log(**{field: value})

    @pytest.mark.parametrize(
        "value",
        ["", "  "],
        ids=["empty", "blank"],
    )
    def test_error_rejects_invalid_event_type(self, value: str) -> None:
        """空文字・空白の event_type が拒否されること."""
        # Act & Assert
        with pytest.raises(ValueError, match="EventType"):
            _valid_log(event_type=value)
