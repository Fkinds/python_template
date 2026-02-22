from __future__ import annotations

import injector
from django.conf import settings

from notifications.infrastructure.adapters.console import ConsoleNotifier
from notifications.infrastructure.adapters.discord import (
    DiscordWebhookNotifier,
)
from notifications.usecases.notify import NotifyAuthorCreatedUseCaseImpl
from notifications.usecases.notify import NotifyBookCreatedUseCaseImpl
from notifications.usecases.protocols import Notifier
from notifications.usecases.protocols import NotifyAuthorCreatedUseCase
from notifications.usecases.protocols import NotifyBookCreatedUseCase

_notifier_override: Notifier | None = None


class NotificationModule(injector.Module):
    """通知の DI バインディングを構成するモジュール."""

    def configure(self, binder: injector.Binder) -> None:
        webhook_url: str = getattr(
            settings,
            "DISCORD_WEBHOOK_URL",
            "",
        )
        if webhook_url:
            binder.bind(
                Notifier,  # type: ignore[type-abstract]
                to=DiscordWebhookNotifier(
                    webhook_url=webhook_url,
                ),
            )
        else:
            binder.bind(
                Notifier,  # type: ignore[type-abstract]
                to=ConsoleNotifier(),
            )

    @injector.provider
    def _book_uc(self, notifier: Notifier) -> NotifyBookCreatedUseCase:
        return NotifyBookCreatedUseCaseImpl(
            notifier=notifier,
        )

    @injector.provider
    def _author_uc(self, notifier: Notifier) -> NotifyAuthorCreatedUseCase:
        return NotifyAuthorCreatedUseCaseImpl(
            notifier=notifier,
        )


def _build_container() -> injector.Injector:
    return injector.Injector([NotificationModule()])


_container: injector.Injector = _build_container()


def get_notifier() -> Notifier:
    """DI コンテナから Notifier を取得するヘルパー."""
    if _notifier_override is not None:
        return _notifier_override
    return _container.get(
        Notifier,  # type: ignore[type-abstract]
    )


def override_notifier(notifier: Notifier | None) -> None:
    """テスト用: Notifier を差し替える."""
    global _notifier_override
    _notifier_override = notifier


def get_book_created_use_case() -> NotifyBookCreatedUseCase:
    """本作成通知ユースケースを取得するヘルパー."""
    if _notifier_override is not None:
        return NotifyBookCreatedUseCaseImpl(
            notifier=_notifier_override,
        )
    return _container.get(
        NotifyBookCreatedUseCase,  # type: ignore[type-abstract]
    )


def get_author_created_use_case() -> NotifyAuthorCreatedUseCase:
    """著者作成通知ユースケースを取得するヘルパー."""
    if _notifier_override is not None:
        return NotifyAuthorCreatedUseCaseImpl(
            notifier=_notifier_override,
        )
    return _container.get(
        NotifyAuthorCreatedUseCase,  # type: ignore[type-abstract]
    )
