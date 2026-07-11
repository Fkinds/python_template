"""Entity 基底クラスの id 同一性のテスト (Small)."""

import uuid

import attrs

from authors.domain.entities.author import Author
from common.domain.entities.supertype import Entity


@attrs.frozen(kw_only=True, eq=False)
class _SampleEntity(Entity):
    name: str = ""


@attrs.frozen(kw_only=True, eq=False)
class _OtherEntity(Entity):
    name: str = ""


class TestEntityEquality:
    def test_happy_equal_when_same_id_ignoring_other_fields(self) -> None:
        # Arrange: 同一型・同一 id なら他フィールドが違っても同一。
        entity_id = uuid.uuid7()
        left = _SampleEntity(id=entity_id, name="a")
        right = _SampleEntity(id=entity_id, name="b")

        # Act & Assert: エンティティ同一性は id 基準。
        assert left == right

    def test_happy_not_equal_when_different_id(self) -> None:
        # Arrange
        left = _SampleEntity(id=uuid.uuid7())
        right = _SampleEntity(id=uuid.uuid7())

        # Act & Assert
        assert left != right

    def test_happy_not_equal_when_different_type_same_id(self) -> None:
        # Arrange: 同じ id でも型が異なれば別エンティティ。
        entity_id = uuid.uuid7()

        # Act & Assert
        assert _SampleEntity(id=entity_id) != _OtherEntity(id=entity_id)

    def test_happy_hash_dedupes_by_id(self) -> None:
        # Arrange: 同一 id は set で 1 件に集約される。
        entity_id = uuid.uuid7()
        left = _SampleEntity(id=entity_id, name="a")
        right = _SampleEntity(id=entity_id, name="b")

        # Act
        result = {left, right}

        # Assert
        assert len(result) == 1

    def test_happy_concrete_subclass_uses_id_identity(self) -> None:
        # Arrange: 実エンティティ Author も id 同一性で判定される。
        author_id = uuid.uuid7()
        left = Author(id=author_id, name="夏目", bio="x")
        right = Author(id=author_id, name="森", bio="y")

        # Act & Assert
        assert left == right
