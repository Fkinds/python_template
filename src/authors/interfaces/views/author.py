"""著者の CRUD ビュー."""

import logging
from collections.abc import Callable
from typing import Any
from typing import ClassVar
from uuid import UUID

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
