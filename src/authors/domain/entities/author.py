"""著者のドメインエンティティ."""

from datetime import datetime

import attrs

from common.domain.entities.base import Entity
from common.domain.validators import not_empty
from common.domain.validators import validate_not_empty


@attrs.frozen(kw_only=True)
class Author(Entity):
    """著者を表すドメインエンティティ.

    id は基底クラス Entity が持つ uuid.UUID を継承する。
    created_at は永続層からの復元時にのみ設定される (新規生成時は None)。
    """

    name: str = attrs.field(validator=[not_empty, validate_not_empty])
    bio: str = ""
    created_at: datetime | None = None
