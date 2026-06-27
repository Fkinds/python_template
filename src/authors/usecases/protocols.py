"""著者ユースケースのポート."""

from typing import Any
from typing import Protocol
from typing import runtime_checkable
from uuid import UUID

from authors.domain.entities.author import Author
from common.usecases.crud import CrudRepository


@runtime_checkable
class AuthorRepository(CrudRepository[Author, UUID], Protocol):
    """著者の永続化ポート."""


@runtime_checkable
class AuthorCrudUseCase(Protocol):
    """著者 CRUD ユースケースのポート."""

    def create(
        self,
        *,
        name: str,
        bio: str,
    ) -> Author:
        """著者を作成する."""
        ...

    def get(self, author_id: UUID) -> Author:
        """著者を取得する (不在時 EntityDoesNotExistError)."""
        ...

    def find_all(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[Author], int]:
        """著者一覧と総件数を返す."""
        ...

    def update(
        self,
        *,
        author_id: UUID,
        fields: dict[str, Any],
    ) -> Author:
        """著者を更新する (不在時 EntityDoesNotExistError)."""
        ...

    def delete(self, author_id: UUID) -> None:
        """著者を削除する (不在時 EntityDoesNotExistError)."""
        ...
