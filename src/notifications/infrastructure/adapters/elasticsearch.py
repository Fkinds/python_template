"""Elasticsearch を使った通知履歴アダプタ."""

import uuid
from datetime import UTC
from datetime import datetime
from typing import Any

from elasticsearch import Elasticsearch
from elasticsearch import NotFoundError

from common.infrastructure.adapters.supertype import Adapter
from common.usecases.protocols import LoggerFactory
from notifications.domain.event_type import EventType
from notifications.domain.notification_channel import NotificationChannel
from notifications.domain.notification_log import NotificationLog
from notifications.domain.notification_status import NotificationStatus

_INDEX_NAME = "notification_logs"

# elasticsearch-py 9 では body= が廃止され、mappings 等を
# キーワード引数で直接渡す。ここは create(mappings=...) に渡す本体。
_INDEX_MAPPING: dict[str, Any] = {
    "properties": {
        "event_type": {"type": "keyword"},
        "message": {"type": "text"},
        "status": {"type": "keyword"},
        "detail": {"type": "text"},
        "recipient": {"type": "keyword"},
        "channel": {"type": "keyword"},
        "retry_count": {"type": "integer"},
        "created_at": {"type": "date"},
    },
}


class ElasticsearchNotificationLogWriterImpl(Adapter):
    """Elasticsearch に通知履歴を書き込むアダプタ."""

    def __init__(
        self,
        *,
        client: Elasticsearch,
        logger_factory: LoggerFactory,
    ) -> None:
        self._client = client
        self._logger = logger_factory.build(name=__name__)
        self._is_index_ensured = False

    def _ensure_index(self) -> None:
        """インデックスが存在しない場合に作成する."""
        if self._is_index_ensured:
            return
        if not self._client.indices.exists(index=_INDEX_NAME):
            self._client.indices.create(
                index=_INDEX_NAME,
                mappings=_INDEX_MAPPING,
            )
            self._logger.info(
                "ES インデックスを作成: %s",
                _INDEX_NAME,
            )
        self._is_index_ensured = True

    def save(
        self,
        *,
        event_type: EventType,
        message: str,
        status: NotificationStatus,
        detail: str,
        recipient: str,
        channel: NotificationChannel,
        retry_count: int,
    ) -> None:
        """通知履歴を Elasticsearch に保存する."""
        doc = {
            "event_type": event_type,
            "message": message,
            "status": status,
            "detail": detail,
            "recipient": recipient,
            "channel": channel,
            "retry_count": retry_count,
            "created_at": datetime.now(tz=UTC).isoformat(),
        }
        self._ensure_index()
        # 同一性は uuid7 で採番し、ES のドキュメント ID として str で保存する。
        self._client.index(
            index=_INDEX_NAME,
            id=str(uuid.uuid7()),
            document=doc,
        )


class ElasticsearchNotificationLogReaderImpl(Adapter):
    """Elasticsearch から通知履歴を読み取るアダプタ."""

    def __init__(
        self,
        *,
        client: Elasticsearch,
        logger_factory: LoggerFactory,
    ) -> None:
        self._client = client
        self._logger = logger_factory.build(name=__name__)

    def find_all(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[NotificationLog], int]:
        """通知履歴の一覧を取得する."""
        from_ = (page - 1) * page_size
        response: Any = self._client.search(
            index=_INDEX_NAME,
            query={"match_all": {}},
            sort=[{"created_at": {"order": "desc"}}],
            from_=from_,
            size=page_size,
        )
        total: int = response["hits"]["total"]["value"]
        logs = [
            self._hit_to_entity(hit=hit) for hit in response["hits"]["hits"]
        ]
        return logs, total

    def find_by_id(self, log_id: str) -> NotificationLog | None:
        """指定IDの通知履歴を取得する."""
        try:
            response: Any = self._client.get(
                index=_INDEX_NAME,
                id=log_id,
            )
        except NotFoundError:
            # 「見つからない」だけを None に変換する。
            # 接続エラー等は握り潰さず呼び出し元へ伝播させる。
            self._logger.debug(
                "通知履歴が見つからない: id=%s",
                log_id,
            )
            return None
        return self._hit_to_entity(hit=response)

    @staticmethod
    def _hit_to_entity(hit: Any) -> NotificationLog:
        """ES ヒットを NotificationLog に変換する.

        本アダプタが当インデックスを所有し、書き込み時に `_id` を
        str(uuid7) で採番する前提のため、読み取り時も UUID として解釈する。
        """
        source: dict[str, Any] = hit["_source"]
        return NotificationLog(
            id=uuid.UUID(hit["_id"]),
            event_type=source["event_type"],
            message=source["message"],
            status=source["status"],
            detail=source.get("detail", ""),
            recipient=source["recipient"],
            channel=source["channel"],
            retry_count=source.get("retry_count", 0),
            created_at=datetime.fromisoformat(source["created_at"]),
        )
