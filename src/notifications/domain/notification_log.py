"""通知履歴のドメインエンティティ."""

from datetime import datetime

import attrs

from common.domain.entities.supertype import Entity
from common.domain.validators import not_empty
from common.domain.validators import validate_not_empty
from notifications.domain.event_type import EventType
from notifications.domain.notification_channel import NotificationChannel
from notifications.domain.notification_status import NotificationStatus


@attrs.frozen(kw_only=True, eq=False)
class NotificationLog(Entity):
    """通知履歴を表すドメインエンティティ.

    id は基底クラス Entity が持つ uuid.UUID を継承する。
    """

    event_type: EventType = attrs.field(
        converter=EventType,
    )
    message: str = attrs.field(
        validator=[not_empty, validate_not_empty],
    )
    status: NotificationStatus = attrs.field(
        converter=NotificationStatus,
    )
    detail: str = ""
    recipient: str = attrs.field(
        validator=[not_empty, validate_not_empty],
    )
    channel: NotificationChannel = attrs.field(
        converter=NotificationChannel,
    )
    retry_count: int = 0
    created_at: datetime = attrs.field(
        validator=attrs.validators.instance_of(datetime),
    )
