from __future__ import annotations

from typing import Any
from typing import ClassVar

import injector
from django.conf import settings
from elasticsearch import Elasticsearch

from common.infrastructure.containers.di import ContainerHolder
from common.infrastructure.factories.logger import LoggerFactoryImpl
from common.usecases.protocols import LoggerFactory
from notifications.domain.notification_channel import NotificationChannel
from notifications.infrastructure.adapters.console import ConsoleNotifierImpl
from notifications.infrastructure.adapters.discord import (
    DiscordWebhookNotifierImpl,
)
from notifications.infrastructure.adapters.elasticsearch import (
    ElasticsearchNotificationLogReaderImpl,
)
from notifications.infrastructure.adapters.elasticsearch import (
    ElasticsearchNotificationLogWriterImpl,
)
from notifications.usecases.notify import NotifyAuthorCreatedUseCaseImpl
from notifications.usecases.notify import NotifyBookCreatedUseCaseImpl
from notifications.usecases.protocols import GetNotificationLogDetailUseCase
from notifications.usecases.protocols import GetNotificationLogsUseCase
from notifications.usecases.protocols import NotificationLogReader
from notifications.usecases.protocols import NotificationLogWriter
from notifications.usecases.protocols import Notifier
from notifications.usecases.protocols import NotifyAuthorCreatedUseCase
from notifications.usecases.protocols import NotifyBookCreatedUseCase
from notifications.usecases.query import GetNotificationLogDetailUseCaseImpl
from notifications.usecases.query import GetNotificationLogsUseCaseImpl


class NotificationModule(injector.Module):
    """通知の DI バインディングを構成するモジュール."""

    _NOTIFIER_MAP: ClassVar[dict[NotificationChannel, type]] = {
        NotificationChannel.DISCORD: DiscordWebhookNotifierImpl,
        NotificationChannel.CONSOLE: ConsoleNotifierImpl,
    }

    def __init__(
        self,
        notifier_override: Notifier | None = None,
        log_writer_override: (NotificationLogWriter | None) = None,
        log_reader_override: (NotificationLogReader | None) = None,
        channel_override: NotificationChannel | None = None,
    ) -> None:
        self._factory = LoggerFactoryImpl()

        if notifier_override is not None:
            self._notifier: Any = notifier_override
            self._channel = channel_override or NotificationChannel.FAKE
        else:
            self._channel = NotificationChannel(
                value=settings.NOTIFICATION_CHANNEL,
            )
            self._notifier = self._build_notifier()

        self._log_writer: Any = (
            log_writer_override or self._es_writer_provider()
        )
        self._log_reader: Any = (
            log_reader_override or self._es_reader_provider()
        )

    def _build_notifier(self) -> Any:
        cls = self._NOTIFIER_MAP[self._channel]
        if cls is DiscordWebhookNotifierImpl:
            return cls(
                webhook_url=settings.DISCORD_WEBHOOK_URL,
                logger_factory=self._factory,
            )
        return cls

    def _es_writer_provider(self) -> Any:
        factory = self._factory

        @injector.provider
        def provide() -> NotificationLogWriter:
            es_url: str = getattr(
                settings,
                "ELASTICSEARCH_URL",
                "http://localhost:9200",
            )
            client = Elasticsearch(hosts=[es_url])
            return ElasticsearchNotificationLogWriterImpl(
                client=client,
                logger_factory=factory,
            )

        return provide

    def _es_reader_provider(self) -> Any:
        factory = self._factory

        @injector.provider
        def provide() -> NotificationLogReader:
            es_url: str = getattr(
                settings,
                "ELASTICSEARCH_URL",
                "http://localhost:9200",
            )
            client = Elasticsearch(hosts=[es_url])
            return ElasticsearchNotificationLogReaderImpl(
                client=client,
                logger_factory=factory,
            )

        return provide

    def configure(self, binder: injector.Binder) -> None:
        binder.bind(
            LoggerFactory,  # type: ignore[type-abstract]
            to=self._factory,
        )
        binder.bind(
            Notifier,  # type: ignore[type-abstract]
            to=self._notifier,
        )
        binder.bind(NotificationChannel, to=self._channel)
        binder.bind(
            NotificationLogWriter,  # type: ignore[type-abstract]
            to=self._log_writer,
        )
        binder.bind(
            NotificationLogReader,  # type: ignore[type-abstract]
            to=self._log_reader,
        )
        binder.bind(
            NotifyBookCreatedUseCase,  # type: ignore[type-abstract]
            to=NotifyBookCreatedUseCaseImpl,
        )
        binder.bind(
            NotifyAuthorCreatedUseCase,  # type: ignore[type-abstract]
            to=NotifyAuthorCreatedUseCaseImpl,
        )
        binder.bind(
            GetNotificationLogsUseCase,  # type: ignore[type-abstract]
            to=GetNotificationLogsUseCaseImpl,
        )
        binder.bind(
            GetNotificationLogDetailUseCase,  # type: ignore[type-abstract]
            to=GetNotificationLogDetailUseCaseImpl,
        )


container = ContainerHolder(NotificationModule())
