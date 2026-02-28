import attrs

from common.domain.validators import not_empty
from common.domain.validators import validate_not_empty


@attrs.frozen(kw_only=True)
class BookCreated:
    """本が作成されたことを表すドメインイベント."""

    title: str = attrs.field(
        validator=[not_empty, validate_not_empty],
    )
    isbn: str = attrs.field(
        validator=[not_empty, validate_not_empty],
    )
    author_name: str = attrs.field(
        validator=[not_empty, validate_not_empty],
    )


@attrs.frozen(kw_only=True)
class AuthorCreated:
    """著者が作成されたことを表すドメインイベント."""

    name: str = attrs.field(
        validator=[not_empty, validate_not_empty],
    )
