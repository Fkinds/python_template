"""通知イベント種別."""

from enum import StrEnum
from enum import auto


class EventType(StrEnum):
    """通知イベントの種別."""

    BOOK_CREATED = auto()
    AUTHOR_CREATED = auto()
