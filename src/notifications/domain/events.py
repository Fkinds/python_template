import attrs


def _validate_not_empty(
    _instance: object,
    attribute: attrs.Attribute[str],
    val: str,
) -> None:
    if not val.strip():
        msg = f"{attribute.name} は空にできません"
        raise ValueError(msg)


_not_empty = attrs.validators.instance_of(str)


@attrs.frozen(kw_only=True)
class BookCreated:
    """本が作成されたことを表すドメインイベント."""

    title: str = attrs.field(
        validator=[_not_empty, _validate_not_empty],
    )
    isbn: str = attrs.field(
        validator=[_not_empty, _validate_not_empty],
    )
    author_name: str = attrs.field(
        validator=[_not_empty, _validate_not_empty],
    )


@attrs.frozen(kw_only=True)
class AuthorCreated:
    """著者が作成されたことを表すドメインイベント."""

    name: str = attrs.field(
        validator=[_not_empty, _validate_not_empty],
    )
