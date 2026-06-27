"""テスト用: メモリ上で著者を保持する Fake リポジトリ.

DI で本物の ORM リポジトリと差し替えて使う (AuthorRepository を満たす)。
"""

from uuid import UUID

from authors.domain.entities.author import Author
from authors.usecases.protocols import AuthorRepository
from common.domain.entities.exceptions import EntityDoesNotExistError


class FakeAuthorRepository(AuthorRepository):
    """著者を保持する Fake リポジトリ (AuthorRepository ポート実装)."""

    def __init__(self, authors: list[Author] | None = None) -> None:
        self._store: dict[UUID, Author] = {
            author.id: author for author in (authors or [])
        }

    def create(self, entity: Author) -> Author:
        self._store[entity.id] = entity
        return entity

    def get(self, entity_id: UUID) -> Author:
        try:
            return self._store[entity_id]
        except KeyError as exc:
            raise EntityDoesNotExistError(str(entity_id)) from exc

    def find_all(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[Author], int]:
        items = list(self._store.values())
        start = (page - 1) * page_size
        return items[start : start + page_size], len(items)

    def update(self, entity: Author) -> Author:
        if entity.id not in self._store:
            raise EntityDoesNotExistError(str(entity.id))
        self._store[entity.id] = entity
        return entity

    def delete(self, entity_id: UUID) -> None:
        if entity_id not in self._store:
            raise EntityDoesNotExistError(str(entity_id))
        del self._store[entity_id]
