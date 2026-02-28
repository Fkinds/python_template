"""通知履歴 API エンドポイントの機能テスト."""

import http
from collections.abc import Generator
from datetime import UTC
from datetime import datetime

import pytest
from rest_framework.test import APIClient

from notifications.domain.event_type import EventType
from notifications.domain.notification_channel import NotificationChannel
from notifications.domain.notification_log import NotificationLog
from notifications.domain.notification_status import NotificationStatus
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


def _make_log(log_id: str = "abc123") -> NotificationLog:
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


@pytest.fixture
def fake_log_reader(db: object) -> Generator[FakeNotificationLogReader]:
    """テスト用の FakeNotificationLogReader を DI に差し込む."""
    reader = FakeNotificationLogReader(logs=[])
    container.override(
        NotificationModule(
            notifier_override=FakeNotifier(),
            log_writer_override=(FakeNotificationLogWriter()),
            log_reader_override=reader,
            channel_override=NotificationChannel.FAKE,
        ),
    )
    yield reader
    container.reset()


@pytest.fixture
def seeded_log_reader(db: object) -> Generator[FakeNotificationLogReader]:
    """データ付きの FakeNotificationLogReader を DI に差し込む."""
    logs = [_make_log(log_id=f"id-{i}") for i in range(5)]
    reader = FakeNotificationLogReader(logs=logs)
    container.override(
        NotificationModule(
            notifier_override=FakeNotifier(),
            log_writer_override=(FakeNotificationLogWriter()),
            log_reader_override=reader,
            channel_override=NotificationChannel.FAKE,
        ),
    )
    yield reader
    container.reset()


class TestNotificationLogListAPI:
    """通知履歴一覧 API のテスト."""

    def test_happy_list_returns_200_with_empty_results(
        self,
        api_client: APIClient,
        fake_log_reader: FakeNotificationLogReader,
    ) -> None:
        """履歴がない場合に空の結果が返ること."""
        # Act
        response = api_client.get("/api/notifications/")

        # Assert
        assert response.status_code == http.HTTPStatus.OK
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_happy_list_returns_200_with_results(
        self,
        api_client: APIClient,
        seeded_log_reader: FakeNotificationLogReader,
    ) -> None:
        """履歴がある場合にデータが返ること."""
        # Act
        response = api_client.get("/api/notifications/")

        # Assert
        assert response.status_code == http.HTTPStatus.OK
        assert response.data["count"] == 5
        assert len(response.data["results"]) == 5

    def test_happy_list_respects_pagination(
        self,
        api_client: APIClient,
        seeded_log_reader: FakeNotificationLogReader,
    ) -> None:
        """ページネーションパラメータが反映されること."""
        # Act
        response = api_client.get("/api/notifications/?page=1&page_size=2")

        # Assert
        assert response.status_code == http.HTTPStatus.OK
        assert response.data["count"] == 5
        assert len(response.data["results"]) == 2

    def test_error_list_rejects_post(
        self,
        api_client: APIClient,
        fake_log_reader: FakeNotificationLogReader,
    ) -> None:
        """POST メソッドが拒否されること."""
        # Act
        response = api_client.post(
            "/api/notifications/",
            data={},
        )

        # Assert
        assert response.status_code == http.HTTPStatus.METHOD_NOT_ALLOWED


class TestNotificationLogDetailAPI:
    """通知履歴詳細 API のテスト."""

    def test_happy_detail_returns_200_with_log(
        self,
        api_client: APIClient,
        seeded_log_reader: FakeNotificationLogReader,
    ) -> None:
        """存在するIDの場合にデータが返ること."""
        # Act
        response = api_client.get("/api/notifications/id-0/")

        # Assert
        assert response.status_code == http.HTTPStatus.OK
        assert response.data["id"] == "id-0"
        assert response.data["event_type"] == "book_created"

    def test_error_detail_returns_404_when_not_found(
        self,
        api_client: APIClient,
        fake_log_reader: FakeNotificationLogReader,
    ) -> None:
        """存在しないIDの場合に404が返ること."""
        # Act
        response = api_client.get("/api/notifications/nonexistent/")

        # Assert
        assert response.status_code == http.HTTPStatus.NOT_FOUND

    def test_error_detail_rejects_post(
        self,
        api_client: APIClient,
        fake_log_reader: FakeNotificationLogReader,
    ) -> None:
        """POST メソッドが拒否されること."""
        # Act
        response = api_client.post(
            "/api/notifications/id-0/",
            data={},
        )

        # Assert
        assert response.status_code == http.HTTPStatus.METHOD_NOT_ALLOWED
