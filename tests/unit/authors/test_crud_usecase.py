"""著者 CRUD ユースケースのテスト (DB 不要・Fake リポジトリ)."""

import uuid

import pytest

from authors.infrastructure.adapters.fake import FakeAuthorRepository
from authors.usecases.crud import AuthorCrudUseCaseImpl
from common.domain.entities.exceptions import EntityDoesNotExistError


def _use_case() -> AuthorCrudUseCaseImpl:
    return AuthorCrudUseCaseImpl(repository=FakeAuthorRepository())


class TestAuthorCrudUseCaseImpl:
    """著者 CRUD ユースケースのテスト."""

    def test_happy_create_mints_uuid_and_persists(self) -> None:
        """作成時に uuid7 が採番され永続化されること."""
        # Arrange
        use_case = _use_case()

        # Act
        author = use_case.create(name="太宰治", bio="走れメロス")

        # Assert
        assert isinstance(author.id, uuid.UUID)
        assert author.name == "太宰治"
        assert use_case.get(author.id).bio == "走れメロス"

    def test_happy_update_partial_keeps_other_fields(self) -> None:
        """部分更新で指定外のフィールドが保たれること."""
        # Arrange
        use_case = _use_case()
        author = use_case.create(name="太宰治", bio="旧略歴")

        # Act
        updated = use_case.update(
            author_id=author.id,
            fields={"bio": "新略歴"},
        )

        # Assert
        assert updated.name == "太宰治"
        assert updated.bio == "新略歴"
        assert updated.id == author.id

    def test_happy_list_paginates(self) -> None:
        """一覧がページネーションされること."""
        # Arrange
        use_case = _use_case()
        for index in range(3):
            use_case.create(name=f"著者{index}", bio="")

        # Act
        page1, total = use_case.find_all(page=1, page_size=2)

        # Assert
        assert total == 3
        assert len(page1) == 2

    def test_happy_delete_removes(self) -> None:
        """削除後に取得すると不在エラーになること."""
        # Arrange
        use_case = _use_case()
        author = use_case.create(name="太宰治", bio="")

        # Act
        use_case.delete(author_id=author.id)

        # Assert
        with pytest.raises(EntityDoesNotExistError):
            use_case.get(author.id)

    def test_error_get_missing_raises(self) -> None:
        """存在しない ID の取得で EntityDoesNotExistError になること."""
        # Arrange
        use_case = _use_case()

        # Act & Assert
        with pytest.raises(EntityDoesNotExistError):
            use_case.get(uuid.uuid7())

    def test_error_update_missing_raises(self) -> None:
        """存在しない ID の更新で EntityDoesNotExistError になること."""
        # Arrange
        use_case = _use_case()

        # Act & Assert
        with pytest.raises(EntityDoesNotExistError):
            use_case.update(
                author_id=uuid.uuid7(),
                fields={"name": "幽霊"},
            )

    def test_error_delete_missing_raises(self) -> None:
        """存在しない ID の削除で EntityDoesNotExistError になること."""
        # Arrange
        use_case = _use_case()

        # Act & Assert
        with pytest.raises(EntityDoesNotExistError):
            use_case.delete(author_id=uuid.uuid7())
