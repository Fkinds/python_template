"""CRUD リポジトリの汎用ポート.

どの資源でも不変な create/get/list/update/delete の形だけを共通化する。
資源固有の振る舞い (エンティティ構築・業務ルール) は各コンテキストの
ユースケースに置く。
"""

from typing import Protocol
from typing import TypeVar

TEntity = TypeVar("TEntity")
# ID は引数位置 (get/delete) でのみ使うため反変。
TId = TypeVar("TId", contravariant=True)


class CrudRepository(Protocol[TEntity, TId]):
    """資源の永続化ポート.

    存在しない ID を扱う get/update/delete は
    ``EntityDoesNotExistError`` を送出する契約とする (取りこぼし防止)。
    """

    def create(self, entity: TEntity) -> TEntity:
        """エンティティを永続化し、保存後のエンティティを返す."""
        ...

    def get(self, entity_id: TId) -> TEntity:
        """ID でエンティティを取得する (不在時 EntityDoesNotExistError)."""
        ...

    def find_all(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[TEntity], int]:
        """ページネーション付きの一覧と総件数を返す."""
        ...

    def update(self, entity: TEntity) -> TEntity:
        """エンティティを更新する (不在時 EntityDoesNotExistError)."""
        ...

    def delete(self, entity_id: TId) -> None:
        """ID でエンティティを削除する (不在時 EntityDoesNotExistError)."""
        ...
