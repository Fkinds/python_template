"""通知履歴の API ビュー."""

from collections.abc import Callable
from typing import ClassVar

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.domain.notification_log import NotificationLog
from notifications.interfaces.serializers.notification_log import (
    NotificationLogSerializer,
)
from notifications.usecases.protocols import GetNotificationLogDetailUseCase
from notifications.usecases.protocols import GetNotificationLogsUseCase


class NotificationLogListView(APIView):
    """通知履歴一覧 API."""

    use_case_resolver: ClassVar[Callable[[], GetNotificationLogsUseCase]]

    def get(self, request: Request) -> Response:
        """通知履歴の一覧を返す."""
        page = int(request.query_params.get("page", "1"))
        page_size = int(request.query_params.get("page_size", "10"))
        use_case = type(self).use_case_resolver()
        logs, total = use_case.execute(
            page=page,
            page_size=page_size,
        )
        serializer = NotificationLogSerializer(instance=logs, many=True)
        return Response(
            {
                "count": total,
                "results": serializer.data,
            }
        )


class NotificationLogDetailView(APIView):
    """通知履歴詳細 API."""

    use_case_resolver: ClassVar[Callable[[], GetNotificationLogDetailUseCase]]

    def get(
        self,
        _request: Request,
        log_id: str,
    ) -> Response:
        """指定IDの通知履歴を返す."""
        use_case = type(self).use_case_resolver()
        log: NotificationLog | None = use_case.execute(log_id=log_id)
        if log is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = NotificationLogSerializer(instance=log)
        return Response(serializer.data)
