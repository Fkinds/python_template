import attrs
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

_allowed_text_validator = RegexValidator(
    regex=r"^[\w\s\u3000-\u303F\u30FC\u30FB\u3001\u3002\uFF01\uFF1F\-,.!?'\"()&+:;/]+$",
    message="使用できない文字が含まれています",
)


def _validate_length(
    instance: "SafeText",
    _attribute: attrs.Attribute[str],
    val: str,
) -> None:
    if len(val) < instance.min_length:
        msg = f"{instance.min_length}文字以上で入力してください"
        raise ValueError(msg)
    if len(val) > instance.max_length:
        msg = f"{instance.max_length}文字以下で入力してください"
        raise ValueError(msg)


def _validate_safe_chars(
    _instance: "SafeText",
    _attribute: attrs.Attribute[str],
    val: str,
) -> None:
    try:
        _allowed_text_validator(val)
    except ValidationError as e:
        raise ValueError(e.message) from e


@attrs.frozen(kw_only=True)
class SafeText:
    """検証済みの安全なテキストを表すバリューオブジェクト."""

    value: str = attrs.field(
        validator=[_validate_length, _validate_safe_chars]
    )
    min_length: int = 1
    max_length: int = 255
