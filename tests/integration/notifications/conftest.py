"""通知統合テスト用の Elasticsearch フィクスチャ."""

from collections.abc import Generator

import pytest
from elasticsearch import Elasticsearch

from common.infrastructure.factories.logger import LoggerFactoryImpl
from notifications.infrastructure.adapters.elasticsearch import (
    ElasticsearchNotificationLogReaderImpl,
)
from notifications.infrastructure.adapters.elasticsearch import (
    ElasticsearchNotificationLogWriterImpl,
)

_Writer = ElasticsearchNotificationLogWriterImpl
_Reader = ElasticsearchNotificationLogReaderImpl

_INDEX_NAME = "notification_logs"
_ES_URL = "http://localhost:9200"


@pytest.fixture(scope="session")
def es_client() -> Generator[Elasticsearch]:
    """セッションスコープの Elasticsearch クライアント."""
    client = Elasticsearch(hosts=[_ES_URL])
    if not client.ping():
        msg = (
            f"Elasticsearch ({_ES_URL}) に接続できません。"
            " docker compose up -d elasticsearch"
            " を実行してください。"
        )
        raise ConnectionError(msg)
    yield client
    client.close()


@pytest.fixture
def es_writer(es_client: Elasticsearch) -> Generator[_Writer]:
    """テストごとにインデックスをクリーンアップする Writer."""
    if es_client.indices.exists(index=_INDEX_NAME):
        es_client.indices.delete(index=_INDEX_NAME)
    factory = LoggerFactoryImpl()
    writer = _Writer(
        client=es_client,
        logger_factory=factory,
    )
    yield writer
    if es_client.indices.exists(index=_INDEX_NAME):
        es_client.indices.delete(index=_INDEX_NAME)


@pytest.fixture
def es_reader(es_client: Elasticsearch) -> _Reader:
    """Reader アダプタ (Writer と同じクライアントを共有)."""
    factory = LoggerFactoryImpl()
    return _Reader(
        client=es_client,
        logger_factory=factory,
    )
