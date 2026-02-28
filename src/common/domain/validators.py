"""attrs 用の共通バリデータ."""

import attrs


def validate_not_empty(
    _instance: object,
    attribute: attrs.Attribute[str],
    val: str,
) -> None:
    """文字列フィールドが空でないことを検証する."""
    if not val.strip():
        msg = f"{attribute.name} は空にできません"
        raise ValueError(msg)


not_empty = attrs.validators.instance_of(str)
