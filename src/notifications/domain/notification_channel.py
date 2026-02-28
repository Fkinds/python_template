"""通知チャネル."""

from enum import StrEnum
from enum import auto


class NotificationChannel(StrEnum):
    """通知の送信先チャネル."""

    DISCORD = auto()
    CONSOLE = auto()
    FAKE = auto()
