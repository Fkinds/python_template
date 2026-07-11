"""Elasticsearch 通知履歴アダプタの統合テスト.

実際の Elasticsearch インスタンスに対してアダプタの動作を検証する.
"""

import time

from elasticsearch import Elasticsearch

from notifications.domain.event_type import EventType
from notifications.domain.notification_channel import NotificationChannel
from notifications.domain.notification_status import NotificationStatus
from notifications.infrastructure.adapters.elasticsearch import (
    ElasticsearchNotificationLogReaderImpl,
)
from notifications.infrastructure.adapters.elasticsearch import (
    ElasticsearchNotificationLogWriterImpl,
)

_Writer = ElasticsearchNotificationLogWriterImpl
_Reader = ElasticsearchNotificationLogReaderImpl

_INDEX_NAME = "notification_logs"


def _refresh_index(client: Elasticsearch) -> None:
    """検索で最新データが返るようにインデックスをリフレッシュする."""
    if client.indices.exists(index=_INDEX_NAME):
        client.indices.refresh(index=_INDEX_NAME)


class TestElasticsearchNotificationLogWriterImpl:
    """ES 書き込みアダプタの統合テスト."""

    def test_happy_save_creates_index_and_document(
        self,
        es_client: Elasticsearch,
        es_writer: _Writer,
    ) -> None:
        """save でインデックスが作成されドキュメントが保存されること."""
        # Act
        es_writer.save(
            event_type=EventType.BOOK_CREATED,
            message="本が登録されました",
            status=NotificationStatus.SUCCESS,
            detail="",
            recipient="discord",
            channel=NotificationChannel.DISCORD,
            retry_count=0,
        )

        # Assert
        assert es_client.indices.exists(
            index=_INDEX_NAME,
        )
        _refresh_index(client=es_client)
        result = es_client.search(
            index=_INDEX_NAME,
            query={"match_all": {}},
        )
        assert result["hits"]["total"]["value"] == 1
        doc = result["hits"]["hits"][0]["_source"]
        assert doc["event_type"] == "book_created"
        assert doc["message"] == "本が登録されました"
        assert doc["status"] == "success"

    def test_happy_save_multiple_documents(
        self,
        es_client: Elasticsearch,
        es_writer: _Writer,
    ) -> None:
        """複数回の save でドキュメントが追加されること."""
        # Act
        es_writer.save(
            event_type=EventType.BOOK_CREATED,
            message="1件目",
            status=NotificationStatus.SUCCESS,
            detail="",
            recipient="discord",
            channel=NotificationChannel.DISCORD,
            retry_count=0,
        )
        es_writer.save(
            event_type=EventType.AUTHOR_CREATED,
            message="2件目",
            status=NotificationStatus.FAILURE,
            detail="タイムアウト",
            recipient="console",
            channel=NotificationChannel.CONSOLE,
            retry_count=1,
        )

        # Assert
        _refresh_index(client=es_client)
        result = es_client.search(
            index=_INDEX_NAME,
            query={"match_all": {}},
        )
        assert result["hits"]["total"]["value"] == 2


class TestElasticsearchNotificationLogReaderImpl:
    """ES 読み取りアダプタの統合テスト."""

    def test_happy_find_all_returns_paginated_results(
        self,
        es_client: Elasticsearch,
        es_writer: _Writer,
        es_reader: _Reader,
    ) -> None:
        """find_all がページネーション付きで結果を返すこと."""
        # Arrange
        es_writer.save(
            event_type=EventType.BOOK_CREATED,
            message="テスト通知",
            status=NotificationStatus.SUCCESS,
            detail="詳細",
            recipient="discord",
            channel=NotificationChannel.DISCORD,
            retry_count=0,
        )
        _refresh_index(client=es_client)

        # Act
        logs, total = es_reader.find_all(
            page=1,
            page_size=10,
        )

        # Assert
        assert total == 1
        assert len(logs) == 1
        assert logs[0].event_type == "book_created"
        assert logs[0].message == "テスト通知"
        assert logs[0].status == "success"
        assert logs[0].channel == "discord"

    def test_happy_find_all_pagination_offset(
        self,
        es_client: Elasticsearch,
        es_writer: _Writer,
        es_reader: _Reader,
    ) -> None:
        """ページ指定で正しいオフセットが適用されること."""
        # Arrange — 3件保存、page_size=2 で page=2 は残り1件
        for i in range(3):
            es_writer.save(
                event_type=EventType.BOOK_CREATED,
                message=f"通知 {i}",
                status=NotificationStatus.SUCCESS,
                detail="",
                recipient="discord",
                channel=NotificationChannel.DISCORD,
                retry_count=0,
            )
            time.sleep(0.01)
        _refresh_index(client=es_client)

        # Act
        logs, total = es_reader.find_all(
            page=2,
            page_size=2,
        )

        # Assert
        assert total == 3
        assert len(logs) == 1

    def test_happy_find_by_id_returns_entity(
        self,
        es_client: Elasticsearch,
        es_writer: _Writer,
        es_reader: _Reader,
    ) -> None:
        """find_by_id が指定IDのエンティティを返すこと."""
        # Arrange
        es_writer.save(
            event_type=EventType.AUTHOR_CREATED,
            message="著者が登録されました",
            status=NotificationStatus.SUCCESS,
            detail="",
            recipient="console",
            channel=NotificationChannel.CONSOLE,
            retry_count=0,
        )
        _refresh_index(client=es_client)
        search_result = es_client.search(
            index=_INDEX_NAME,
            query={"match_all": {}},
        )
        doc_id: str = search_result["hits"]["hits"][0]["_id"]

        # Act
        result = es_reader.find_by_id(log_id=doc_id)

        # Assert
        assert result is not None
        assert str(result.id) == doc_id
        assert result.event_type == "author_created"
        assert result.message == "著者が登録されました"
        assert result.channel == "console"
        assert result.recipient == "console"
        assert result.retry_count == 0
        assert result.created_at is not None

    # lint-fixme: ParamLineBreak: 79文字制限で改行が必要
    def test_happy_find_by_id_returns_none_on_missing(
        self, es_reader: _Reader
    ) -> None:
        """存在しないIDの場合にNoneを返すこと."""
        # Act
        result = es_reader.find_by_id(
            log_id="nonexistent-id-12345",
        )

        # Assert
        assert result is None


class TestElasticsearchRoundTrip:
    """Writer → Reader のラウンドトリップテスト."""

    def test_happy_write_then_read_round_trip(
        self,
        es_client: Elasticsearch,
        es_writer: _Writer,
        es_reader: _Reader,
    ) -> None:
        """Writer で保存したデータが Reader で正確に取得できること."""
        # Arrange
        es_writer.save(
            event_type=EventType.BOOK_CREATED,
            message="ラウンドトリップテスト",
            status=NotificationStatus.FAILURE,
            detail="テスト失敗詳細",
            recipient="discord",
            channel=NotificationChannel.DISCORD,
            retry_count=3,
        )
        _refresh_index(client=es_client)

        # Act
        logs, total = es_reader.find_all(
            page=1,
            page_size=10,
        )

        # Assert
        assert total == 1
        assert len(logs) == 1
        log = logs[0]
        assert log.event_type == "book_created"
        assert log.message == "ラウンドトリップテスト"
        assert log.status == "failure"
        assert log.detail == "テスト失敗詳細"
        assert log.recipient == "discord"
        assert log.channel == "discord"
        assert log.retry_count == 3
        assert log.created_at is not None
