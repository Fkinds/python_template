"""著者リポジトリ (Django ORM)."""

from uuid import UUID

from authors.domain.entities.author import Author as AuthorEntity
from authors.models import Author as AuthorModel
from authors.usecases.protocols import AuthorRepository
from common.domain.entities.exceptions import EntityDoesNotExistError
from common.interfaces.repositories.supertype import Repository


class AuthorRepositoryImpl(Repository, AuthorRepository):
    """著者の永続化を担う ORM リポジトリ (AuthorRepository ポートを実装)."""

    def create(self, entity: AuthorEntity) -> AuthorEntity:
        """ドメインで採番済みの id を用いて永続化する."""
        model = AuthorModel.objects.create(
            id=entity.id,
            name=entity.name,
            bio=entity.bio,
        )
        return self._to_entity(model)

    def get(self, entity_id: UUID) -> AuthorEntity:
        """ID で取得する (不在時 EntityDoesNotExistError)."""
        return self._to_entity(self._get_model(entity_id))

    def find_all(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[AuthorEntity], int]:
        """ページネーション付きの一覧と総件数を返す."""
        queryset = AuthorModel.objects.all()
        total = queryset.count()
        start = (page - 1) * page_size
        models = queryset[start : start + page_size]
        return [self._to_entity(model) for model in models], total

    def update(self, entity: AuthorEntity) -> AuthorEntity:
        """name/bio を更新する (不在時 EntityDoesNotExistError)."""
        updated = AuthorModel.objects.filter(pk=entity.id).update(
            name=entity.name,
            bio=entity.bio,
        )
        if updated == 0:
            msg = f"著者が見つかりません: id={entity.id}"
            raise EntityDoesNotExistError(msg)
        return entity

    def delete(self, entity_id: UUID) -> None:
        """ID で削除する (不在時 EntityDoesNotExistError)."""
        self._get_model(entity_id).delete()

    def _get_model(self, entity_id: UUID) -> AuthorModel:
        try:
            return AuthorModel.objects.get(pk=entity_id)
        except AuthorModel.DoesNotExist as exc:
            msg = f"著者が見つかりません: id={entity_id}"
            raise EntityDoesNotExistError(msg) from exc

    @staticmethod
    def _to_entity(model: AuthorModel) -> AuthorEntity:
        return AuthorEntity(
            id=model.id,
            name=model.name,
            bio=model.bio,
            created_at=model.created_at,
        )
