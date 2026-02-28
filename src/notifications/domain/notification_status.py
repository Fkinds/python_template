"""通知ステータス."""

from enum import StrEnum
from enum import auto


class NotificationStatus(StrEnum):
    """通知の送信結果ステータス."""

    SUCCESS = auto()
    FAILURE = auto()
