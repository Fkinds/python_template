"""著者 CRUD ユースケース."""

from typing import Any
from uuid import UUID

import attrs
import injector

from authors.domain.entities.author import Author
from authors.usecases.protocols import AuthorRepository


class AuthorCrudUseCaseImpl:
    """著者 CRUD のユースケース実装."""

    @injector.inject
    def __init__(self, repository: AuthorRepository) -> None:
        self._repository = repository

    def create(
        self,
        *,
        name: str,
        bio: str,
    ) -> Author:
        """著者を作成する (id は uuid7 で自動採番)."""
        author = Author(name=name, bio=bio)
        return self._repository.create(author)

    def get(self, author_id: UUID) -> Author:
        """著者を取得する."""
        return self._repository.get(author_id)

    def find_all(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[Author], int]:
        """著者一覧と総件数を返す."""
        return self._repository.find_all(page=page, page_size=page_size)

    def update(
        self,
        *,
        author_id: UUID,
        fields: dict[str, Any],
    ) -> Author:
        """既存著者に検証済みフィールドを反映して更新する."""
        # 不在なら get が EntityDoesNotExistError を送出する (-> 404)。
        current = self._repository.get(author_id)
        updated = attrs.evolve(current, **fields)
        return self._repository.update(updated)

    def delete(self, author_id: UUID) -> None:
        """著者を削除する."""
        self._repository.delete(author_id)
