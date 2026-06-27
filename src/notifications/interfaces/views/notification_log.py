"""通知履歴の API ビュー."""

from collections.abc import Callable
from typing import Any
from typing import ClassVar

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
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


# 一覧は {count, results} のエンベロープで返すため、OpenAPI 用に明示する。
# many=False で list 検出による配列ラップ (heuristic) を抑止する。
@extend_schema_serializer(
    many=False,
    component_name="NotificationLogListResponse",
)
class _NotificationLogListResponse(serializers.Serializer[Any]):
    count = serializers.IntegerField()
    results = NotificationLogSerializer(many=True)


# ページングは query_params から直接読むため明示する。
_PAGE_PARAMS = [
    OpenApiParameter(
        name="page",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description="ページ番号 (1 以上)",
    ),
    OpenApiParameter(
        name="page_size",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description="1 ページあたりの件数 (1 以上)",
    ),
]


class NotificationLogListView(APIView):
    """通知履歴一覧 API."""

    use_case_resolver: ClassVar[Callable[[], GetNotificationLogsUseCase]]

    @extend_schema(
        operation_id="notifications_list",
        summary="通知履歴一覧",
        parameters=_PAGE_PARAMS,
        responses=_NotificationLogListResponse,
    )
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

    @extend_schema(
        operation_id="notifications_retrieve",
        summary="通知履歴詳細",
        responses={
            200: NotificationLogSerializer,
            404: OpenApiResponse(description="通知履歴が存在しない"),
        },
    )
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
