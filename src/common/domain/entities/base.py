"""ドメイン層の基底クラス."""

import uuid

import attrs


@attrs.frozen(kw_only=True)
class Entity:
    """エンティティの基底クラス.

    UUID の id を持つ。等価判定は attrs デフォルト (全属性) であり、
    id 基準の同一性ではない点に注意 (現状は不変スナップショット用途)。
    """

    # uuid7: 時系列順で DB インデックス効率が良い。
    # 新規生成時は自動採番し、永続層からの復元時は既存 ID を渡す。
    id: uuid.UUID = attrs.field(
        factory=uuid.uuid7,
        validator=attrs.validators.instance_of(uuid.UUID),
    )


class ValueObject:
    """バリューオブジェクトの基底クラス."""

    pass
