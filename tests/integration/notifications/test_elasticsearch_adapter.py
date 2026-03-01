from datetime import UTC
from datetime import datetime
from unittest.mock import MagicMock

from common.infrastructure.factories.logger import LoggerFactoryImpl
from notifications.domain.event_type import EventType
from notifications.domain.notification_channel import NotificationChannel
from notifications.domain.notification_status import NotificationStatus
from notifications.infrastructure.adapters.elasticsearch import (
    ElasticsearchNotificationLogReaderImpl,
)
from notifications.infrastructure.adapters.elasticsearch import (
    ElasticsearchNotificationLogWriterImpl,
)

_factory = LoggerFactoryImpl()


def _mock_client(index_exists: bool = True) -> MagicMock:
    """テスト用の Elasticsearch クライアント mock."""
    client = MagicMock()
    client.indices.exists.return_value = index_exists
    return client


class TestElasticsearchNotificationLogWriterImpl:
    """ES 書き込みアダプタのテスト."""

    def test_happy_ensure_index_creates_when_missing(
        self,
    ) -> None:
        """初回 save 時にインデックスが作成されること."""
        # Arrange
        client = _mock_client(index_exists=False)
        writer = ElasticsearchNotificationLogWriterImpl(
            client=client,
            logger_factory=_factory,
        )

        # Act
        writer.save(
            event_type=EventType.BOOK_CREATED,
            message="テスト",
            status=NotificationStatus.SUCCESS,
            detail="",
            recipient="discord",
            channel=NotificationChannel.DISCORD,
            retry_count=0,
        )

        # Assert
        client.indices.create.assert_called_once()

    def test_happy_ensure_index_skips_when_exists(
        self,
    ) -> None:
        """インデックスが存在する場合は作成しないこと."""
        # Arrange
        client = _mock_client(index_exists=True)
        writer = ElasticsearchNotificationLogWriterImpl(
            client=client,
            logger_factory=_factory,
        )

        # Act
        writer.save(
            event_type=EventType.BOOK_CREATED,
            message="テスト",
            status=NotificationStatus.SUCCESS,
            detail="",
            recipient="discord",
            channel=NotificationChannel.DISCORD,
            retry_count=0,
        )

        # Assert
        client.indices.create.assert_not_called()

    def test_happy_save_indexes_document(self) -> None:
        """save でドキュメントが index されること."""
        # Arrange
        client = _mock_client()
        writer = ElasticsearchNotificationLogWriterImpl(
            client=client,
            logger_factory=_factory,
        )

        # Act
        writer.save(
            event_type=EventType.BOOK_CREATED,
            message="本が登録されました",
            status=NotificationStatus.SUCCESS,
            detail="",
            recipient="discord",
            channel=NotificationChannel.DISCORD,
            retry_count=0,
        )

        # Assert
        client.index.assert_called_once()
        call_kwargs = client.index.call_args
        assert call_kwargs.kwargs["index"] == "notification_logs"
        body = call_kwargs.kwargs["body"]
        assert body["event_type"] == "book_created"
        assert body["status"] == "success"


class TestElasticsearchNotificationLogReaderImpl:
    """ES 読み取りアダプタのテスト."""

    def test_happy_find_all_returns_paginated_results(
        self,
    ) -> None:
        """find_all がページネーション付き結果を返すこと."""
        # Arrange
        client = _mock_client()
        client.search.return_value = {
            "hits": {
                "total": {"value": 1},
                "hits": [
                    {
                        "_id": "doc-1",
                        "_source": {
                            "event_type": "book_created",
                            "message": "テスト",
                            "status": "success",
                            "detail": "",
                            "recipient": "discord",
                            "channel": "discord",
                            "retry_count": 0,
                            "created_at": "2026-01-01T00:00:00+00:00",
                        },
                    }
                ],
            }
        }
        reader = ElasticsearchNotificationLogReaderImpl(
            client=client,
            logger_factory=_factory,
        )

        # Act
        logs, total = reader.find_all(page=1, page_size=10)

        # Assert
        assert total == 1
        assert len(logs) == 1
        assert logs[0].id == "doc-1"
        assert logs[0].event_type == "book_created"
        assert logs[0].created_at == datetime(2026, 1, 1, tzinfo=UTC)

    def test_happy_find_by_id_returns_entity(
        self,
    ) -> None:
        """find_by_id が指定IDのエンティティを返すこと."""
        # Arrange
        client = _mock_client()
        client.get.return_value = {
            "_id": "doc-1",
            "_source": {
                "event_type": "author_created",
                "message": "著者が登録されました",
                "status": "success",
                "detail": "",
                "recipient": "console",
                "channel": "console",
                "retry_count": 0,
                "created_at": "2026-01-01T00:00:00+00:00",
            },
        }
        reader = ElasticsearchNotificationLogReaderImpl(
            client=client,
            logger_factory=_factory,
        )

        # Act
        result = reader.find_by_id(log_id="doc-1")

        # Assert
        assert result is not None
        assert result.id == "doc-1"
        assert result.channel == "console"

    def test_happy_find_by_id_returns_none_on_missing(
        self,
    ) -> None:
        """存在しないIDの場合にNoneを返すこと."""
        # Arrange
        client = _mock_client()
        client.get.side_effect = Exception("ドキュメント未検出")
        reader = ElasticsearchNotificationLogReaderImpl(
            client=client,
            logger_factory=_factory,
        )

        # Act
        result = reader.find_by_id(log_id="nonexistent")

        # Assert
        assert result is None

    def test_happy_find_all_pagination_offset(
        self,
    ) -> None:
        """find_all が正しい from 値で検索すること."""
        # Arrange
        client = _mock_client()
        client.search.return_value = {
            "hits": {"total": {"value": 0}, "hits": []}
        }
        reader = ElasticsearchNotificationLogReaderImpl(
            client=client,
            logger_factory=_factory,
        )

        # Act
        reader.find_all(page=3, page_size=5)

        # Assert
        call_kwargs = client.search.call_args
        body = call_kwargs.kwargs["body"]
        assert body["from"] == 10
        assert body["size"] == 5
