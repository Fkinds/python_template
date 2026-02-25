"""common.domain.exceptions のテスト."""

import pytest

from common.domain.entities.exceptions import EntityDoesNotExistError
from common.domain.entities.exceptions import EntityError
from common.domain.entities.exceptions import GenerateRepositoryError
from common.infrastructure.adapters.exceptions import AdapterError
from common.infrastructure.adapters.exceptions import GenerateAdapterError
from common.infrastructure.factories.exceptions import FactoryError
from common.infrastructure.factories.exceptions import GenerateFactoryError


class TestExceptionHierarchy:
    """例外クラスの継承関係のテスト."""

    def test_happy_entity_does_not_exist_is_entity_error(
        self,
    ) -> None:
        """EntityDoesNotExistError は EntityError のサブクラスであること."""
        assert issubclass(EntityDoesNotExistError, EntityError)

    def test_happy_generate_repository_error_is_entity_error(
        self,
    ) -> None:
        """GenerateRepositoryError は EntityError のサブクラスであること."""
        assert issubclass(GenerateRepositoryError, EntityError)

    def test_happy_entity_error_is_exception(self) -> None:
        """EntityError は Exception のサブクラスであること."""
        assert issubclass(EntityError, Exception)

    def test_happy_generate_adapter_error_is_adapter_error(
        self,
    ) -> None:
        """GenerateAdapterError は AdapterError のサブクラスであること."""
        assert issubclass(GenerateAdapterError, AdapterError)

    def test_happy_adapter_error_is_exception(self) -> None:
        """AdapterError は Exception のサブクラスであること."""
        assert issubclass(AdapterError, Exception)

    def test_happy_generate_factory_error_is_factory_error(
        self,
    ) -> None:
        """GenerateFactoryError は FactoryError のサブクラスであること."""
        assert issubclass(GenerateFactoryError, FactoryError)

    def test_happy_factory_error_is_exception(self) -> None:
        """FactoryError は Exception のサブクラスであること."""
        assert issubclass(FactoryError, Exception)


class TestExceptionRaiseAndCatch:
    """例外の送出とキャッチのテスト."""

    def test_happy_entity_does_not_exist_carries_message(
        self,
    ) -> None:
        """EntityDoesNotExistError がメッセージを保持すること."""
        with pytest.raises(EntityDoesNotExistError, match="book_id=42"):
            raise EntityDoesNotExistError("book_id=42 が見つかりません")

    def test_happy_caught_as_base_entity_error(self) -> None:
        """EntityDoesNotExistError が EntityError でキャッチできること."""
        with pytest.raises(EntityError):
            raise EntityDoesNotExistError("not found")

    def test_happy_generate_repository_caught_as_entity_error(
        self,
    ) -> None:
        """GenerateRepositoryError が EntityError でキャッチできること."""
        with pytest.raises(EntityError):
            raise GenerateRepositoryError("リポジトリ生成失敗")

    def test_happy_generate_adapter_caught_as_adapter_error(
        self,
    ) -> None:
        """GenerateAdapterError が AdapterError でキャッチできること."""
        with pytest.raises(AdapterError):
            raise GenerateAdapterError("アダプタ生成失敗")

    def test_happy_generate_factory_caught_as_factory_error(
        self,
    ) -> None:
        """GenerateFactoryError が FactoryError でキャッチできること."""
        with pytest.raises(FactoryError):
            raise GenerateFactoryError("ファクトリ生成失敗")

    def test_happy_exception_chaining_preserved(self) -> None:
        """例外チェーンが保持されること."""
        # Arrange
        original = ValueError("元の原因")
        chained = EntityDoesNotExistError("ラップ")
        chained.__cause__ = original

        # Act & Assert
        with pytest.raises(EntityDoesNotExistError) as exc_info:
            raise chained
        assert exc_info.value.__cause__ is original
