"""通知履歴の URL パターン (composition root)."""

from django.urls import path

from notifications.infrastructure.containers.notificaton import container
from notifications.interfaces.views.notification_log import (
    NotificationLogDetailView,
)
from notifications.interfaces.views.notification_log import (
    NotificationLogListView,
)
from notifications.usecases.protocols import GetNotificationLogDetailUseCase
from notifications.usecases.protocols import GetNotificationLogsUseCase

NotificationLogListView.use_case_resolver = lambda: container.injector.get(
    GetNotificationLogsUseCase,  # type: ignore[type-abstract]
)

NotificationLogDetailView.use_case_resolver = lambda: container.injector.get(
    GetNotificationLogDetailUseCase,  # type: ignore[type-abstract]
)

urlpatterns = [
    path(
        "notifications/",
        NotificationLogListView.as_view(),
        name="notification-log-list",
    ),
    path(
        "notifications/<str:log_id>/",
        NotificationLogDetailView.as_view(),
        name="notification-log-detail",
    ),
]
