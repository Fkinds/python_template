"""著者の CRUD ビュー."""

import logging
from collections.abc import Callable
from typing import Any
from typing import ClassVar
from uuid import UUID

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_serializer
from drf_spectacular.utils import extend_schema_view
from rest_framework import serializers

from authors.domain.entities.author import Author
from authors.interfaces.deserializers.author import AuthorDeserializer
from authors.interfaces.serializers.author import AuthorSerializer
from authors.usecases.protocols import AuthorCrudUseCase
from common.domain.entities.exceptions import EntityDoesNotExistError
from common.interfaces.views.crud import CrudViewSet
from notifications.domain.events import AuthorCreated
from notifications.domain.results import NotificationProblem
from notifications.infrastructure.containers.notificaton import container
from notifications.usecases.protocols import NotifyAuthorCreatedUseCase

logger = logging.getLogger(__name__)


# 一覧は {count, results} のエンベロープで返すため、OpenAPI 用に明示する。
# many=False で list アクションの配列ラップ (heuristic) を抑止する。
@extend_schema_serializer(many=False, component_name="AuthorListResponse")
class _AuthorListResponse(serializers.Serializer[Any]):
    count = serializers.IntegerField()
    results = AuthorSerializer(many=True)


# 一覧アクションのページングは query_params から直接読むため明示する。
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

# 単一資源を指すパスパラメータ (UUID) を明示する。
_ID_PARAM = OpenApiParameter(
    name="id",
    type=OpenApiTypes.UUID,
    location=OpenApiParameter.PATH,
    description="著者ID (UUID)",
)


@extend_schema_view(
    list=extend_schema(
        summary="著者一覧",
        parameters=_PAGE_PARAMS,
        responses=_AuthorListResponse,
    ),
    create=extend_schema(
        summary="著者作成",
        request=AuthorDeserializer,
        responses={201: AuthorSerializer},
    ),
    retrieve=extend_schema(
        summary="著者取得",
        parameters=[_ID_PARAM],
        responses=AuthorSerializer,
    ),
    update=extend_schema(
        summary="著者更新",
        parameters=[_ID_PARAM],
        request=AuthorDeserializer,
        responses=AuthorSerializer,
    ),
    partial_update=extend_schema(
        summary="著者部分更新",
        parameters=[_ID_PARAM],
        request=AuthorDeserializer,
        responses=AuthorSerializer,
    ),
    destroy=extend_schema(
        summary="著者削除",
        parameters=[_ID_PARAM],
        responses={204: OpenApiResponse(description="削除成功")},
    ),
)
class AuthorViewSet(CrudViewSet):
    """著者 CRUD API."""

    output_serializer_class = AuthorSerializer
    input_deserializer_class = AuthorDeserializer

    use_case_resolver: ClassVar[Callable[[], AuthorCrudUseCase]]

    def perform_create(self, data: dict[str, Any]) -> Author:
        author = self._use_case().create(
            name=data["name"],
            bio=data.get("bio", ""),
        )
        self._notify_created(author)
        return author

    def perform_get(self, pk: str) -> Author:
        return self._use_case().get(author_id=self._to_uuid(pk))

    def perform_list(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[Author], int]:
        return self._use_case().find_all(page=page, page_size=page_size)

    def perform_update(
        self,
        pk: str,
        data: dict[str, Any],
    ) -> Author:
        return self._use_case().update(
            author_id=self._to_uuid(pk),
            fields=data,
        )

    def perform_delete(self, pk: str) -> None:
        self._use_case().delete(author_id=self._to_uuid(pk))

    def _use_case(self) -> AuthorCrudUseCase:
        return type(self).use_case_resolver()

    @staticmethod
    def _to_uuid(pk: str) -> UUID:
        # 不正な UUID は「存在しない資源」として 404 に倒す。
        try:
            return UUID(pk)
        except ValueError as exc:
            msg = f"不正なID: {pk}"
            raise EntityDoesNotExistError(msg) from exc

    def _notify_created(self, author: Author) -> None:
        """作成時に AuthorCreated 通知を送る (失敗しても作成は成功)."""
        event = AuthorCreated(name=author.name)
        result = container.injector.get(
            NotifyAuthorCreatedUseCase,  # type: ignore[type-abstract]
        ).execute(event=event)
        if isinstance(result, NotificationProblem):
            logger.warning("通知送信に失敗しました: %s", result.detail)
