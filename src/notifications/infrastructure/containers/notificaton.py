from __future__ import annotations

import injector
from django.conf import settings

from common.infrastructure.containers.di import ContainerHolder
from common.infrastructure.factories.logger import LoggerFactoryImpl
from common.usecases.protocols import LoggerFactory
from notifications.infrastructure.adapters.console import ConsoleNotifierImpl
from notifications.infrastructure.adapters.discord import (
    DiscordWebhookNotifierImpl,
)
from notifications.usecases.notify import NotifyAuthorCreatedUseCaseImpl
from notifications.usecases.notify import NotifyBookCreatedUseCaseImpl
from notifications.usecases.protocols import Notifier
from notifications.usecases.protocols import NotifyAuthorCreatedUseCase
from notifications.usecases.protocols import NotifyBookCreatedUseCase


class NotificationModule(injector.Module):
    """通知の DI バインディングを構成するモジュール."""

    def __init__(self, notifier_override: Notifier | None = None) -> None:
        self._notifier_override = notifier_override

    def configure(self, binder: injector.Binder) -> None:
        factory = LoggerFactoryImpl()
        binder.bind(
            LoggerFactory,  # type: ignore[type-abstract]
            to=factory,
        )

        if self._notifier_override is not None:
            binder.bind(
                Notifier,  # type: ignore[type-abstract]
                to=self._notifier_override,
            )
        else:
            webhook_url: str = getattr(
                settings,
                "DISCORD_WEBHOOK_URL",
                "",
            )
            if webhook_url:
                binder.bind(
                    Notifier,  # type: ignore[type-abstract]
                    to=DiscordWebhookNotifierImpl(
                        webhook_url=webhook_url,
                        logger_factory=factory,
                    ),
                )
            else:
                binder.bind(
                    Notifier,  # type: ignore[type-abstract]
                    to=ConsoleNotifierImpl,
                )

        binder.bind(
            NotifyBookCreatedUseCase,  # type: ignore[type-abstract]
            to=NotifyBookCreatedUseCaseImpl,
        )
        binder.bind(
            NotifyAuthorCreatedUseCase,  # type: ignore[type-abstract]
            to=NotifyAuthorCreatedUseCaseImpl,
        )


container = ContainerHolder(NotificationModule())
