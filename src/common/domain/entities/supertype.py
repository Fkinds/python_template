"""ドメイン層の基底クラス."""

import uuid

import attrs


@attrs.frozen(kw_only=True, eq=False)
class Entity:
    """エンティティの基底クラス.

    等価性は id 同一性で判定する (同じ型かつ同じ id なら等価)。
    attrs の全属性等価を避けるため eq=False とし、__eq__ / __hash__
    を明示定義している。

    重要: 本クラスを継承する具象エンティティは必ず
    ``@attrs.frozen(kw_only=True, eq=False)`` を付けること。
    eq を再生成させると全属性等価に戻ってしまう。
    """

    # uuid7: 時系列順で DB インデックス効率が良い。
    # 新規生成時は自動採番し、永続層からの復元時は既存 ID を渡す。
    id: uuid.UUID = attrs.field(
        factory=uuid.uuid7,
        validator=attrs.validators.instance_of(uuid.UUID),
    )

    def __eq__(self, other: object) -> bool:
        # 同一クラスかつ同一 id のときのみ等価 (エンティティ同一性)。
        if not isinstance(other, Entity) or type(self) is not type(other):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))


class ValueObject:
    """バリューオブジェクトの基底クラス."""

    pass
